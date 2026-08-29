from __future__ import annotations

from datetime import date

from app.sources.ssc_calendar import parse_indian_date


def test_full_date_is_exact():
    parsed, text, month_only = parse_indian_date("16 March 2026")
    assert parsed == date(2026, 3, 16)
    assert month_only is False
    assert text == "16 March 2026"


def test_month_only_is_flagged_and_keeps_original_words():
    parsed, text, month_only = parse_indian_date("March 2026")
    assert parsed == date(2026, 3, 1)
    assert month_only is True
    assert text == "March 2026"


def test_month_range_keeps_the_words_it_was_given():
    parsed, text, month_only = parse_indian_date("May – June 2026")
    assert month_only is True
    assert "May" in text


def test_empty_cell_gives_nothing():
    parsed, text, month_only = parse_indian_date("   ")
    assert parsed is None
    assert text == ""
    assert month_only is False


def test_unreadable_text_is_not_guessed():
    parsed, text, month_only = parse_indian_date("to be announced")
    assert parsed is None
    assert month_only is False
