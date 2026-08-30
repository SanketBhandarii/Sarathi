from __future__ import annotations

from app.apply.links import ApplyLink, is_official_host, official_urls_in_pages, urls_in_pages
from app.extraction.document import Page

JOB_SITES = [
    "https://www.freejobalert.com/ibps-po",
    "https://sarkariresult.com/apply",
    "http://adserver.example.net/click?to=ibps",
    "https://ibps.in.fake-domain.com/apply",
]

OFFICIAL = [
    "https://ssc.gov.in/candidate-portal",
    "https://upsconline.nic.in/ora/",
    "https://www.ibps.in/",
]


def test_job_websites_are_never_treated_as_official():
    for url in JOB_SITES:
        assert is_official_host(url) is False, url


def test_government_domains_are_official():
    for url in OFFICIAL:
        assert is_official_host(url) is True, url


def test_a_lookalike_domain_is_rejected():
    assert is_official_host("https://ssc.gov.in.evil.example/apply") is False


def test_urls_are_pulled_out_of_the_page_text():
    pages = [Page(number=1, text="Apply at https://ssc.gov.in/apply before the last date.")]
    assert "https://ssc.gov.in/apply" in urls_in_pages(pages)


def test_trailing_punctuation_is_trimmed():
    pages = [Page(number=1, text="see https://ssc.gov.in/apply. Then wait.")]
    assert "https://ssc.gov.in/apply" in urls_in_pages(pages)


def test_only_official_urls_survive_the_filter():
    pages = [
        Page(
            number=1,
            text="Apply at https://ssc.gov.in/apply or https://freejobalert.com/x for details.",
        )
    ]
    found = official_urls_in_pages(pages)
    assert found == ["https://ssc.gov.in/apply"]


def test_an_unreachable_official_link_is_not_shown_as_ready():
    link = ApplyLink(
        url="https://ssc.gov.in/gone", label="x", source_id="ssc",
        is_official=True, reachable=False, http_status=404,
    )
    assert link.can_show is False
    assert "not opening" in link.note


def test_a_reachable_official_link_says_no_advertisements():
    link = ApplyLink(
        url="https://ssc.gov.in/apply", label="x", source_id="ssc",
        is_official=True, reachable=True, http_status=200,
    )
    assert link.can_show is True
    assert "No advertisements" in link.note
