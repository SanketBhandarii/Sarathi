from __future__ import annotations

from datetime import date

from app.extraction.windows import find_last_date_to_apply

IBPS_REAL_SENTENCE = (
    "Candidates can apply online only and no other mode of application will be accepted. "
    "Application Fees/ Intimation Charges [Online payment from 01.07.2026 to 21.07.2026, "
    "both dates inclusive] shall be as follows."
)


def test_it_reads_the_end_of_a_real_range_not_the_start():
    found = find_last_date_to_apply([IBPS_REAL_SENTENCE])
    assert found is not None
    assert found.happens_on == date(2026, 7, 21)
    assert found.citation.page == 1
    assert "21.07.2026" in found.citation.quote


def test_it_quotes_the_sentence_it_read_the_date_from():
    found = find_last_date_to_apply(["filler.", IBPS_REAL_SENTENCE])
    assert found is not None
    assert found.citation.page == 2
    assert "Online payment from" in found.citation.quote


def test_a_range_about_something_other_than_applying_is_ignored():
    text = "The result will remain valid from 01.07.2026 to 20.07.2027 for all purposes."
    assert find_last_date_to_apply([text]) is None


def test_it_reads_a_plainly_stated_last_date():
    text = "The last date for submission of online applications is 11.09.2026."
    found = find_last_date_to_apply([text])
    assert found is not None
    assert found.happens_on == date(2026, 9, 11)


def test_a_document_that_never_states_a_date_gets_nothing():
    text = (
        "Age will be determined as on the last date of submission of applications. "
        "After closing date for submission of online applications, a three days window "
        "has been kept for modification."
    )
    assert find_last_date_to_apply([text]) is None


def test_it_takes_the_earliest_closing_when_a_document_offers_several():
    pages = [
        "Online registration from 01.07.2026 to 21.07.2026 for all candidates.",
        "Application editing is open from 01.07.2026 to 24.07.2026 for all candidates.",
    ]
    found = find_last_date_to_apply(pages)
    assert found is not None
    assert found.happens_on == date(2026, 7, 21)


def test_slashes_and_dashes_are_read_too():
    assert find_last_date_to_apply(
        ["Registration from 01/07/2026 to 21/07/2026."]
    ).happens_on == date(2026, 7, 21)
    assert find_last_date_to_apply(
        ["Registration from 01-07-2026 to 21-07-2026."]
    ).happens_on == date(2026, 7, 21)


def test_an_impossible_date_is_not_believed():
    assert find_last_date_to_apply(["Registration from 01.07.2026 to 32.13.2026."]) is None


def test_it_never_guesses_from_an_empty_document():
    assert find_last_date_to_apply([]) is None
    assert find_last_date_to_apply([""]) is None
