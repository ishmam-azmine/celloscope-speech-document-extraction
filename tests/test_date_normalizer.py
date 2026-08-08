from app.services.date_normalizer import normalize_date


def test_normalizes_iso_date():
    assert normalize_date("2026-08-08") == "2026-08-08"


def test_normalizes_unambiguous_day_first_numeric_date():
    assert normalize_date("13/08/2026") == "2026-08-13"


def test_normalizes_unambiguous_month_first_numeric_date():
    assert normalize_date("08/13/2026") == "2026-08-13"


def test_normalizes_written_month_date():
    assert normalize_date("August 8, 2026") == "2026-08-08"


def test_preserves_ambiguous_numeric_date():
    assert normalize_date("08/09/2026") == "08/09/2026"


def test_preserves_unknown_date_format():
    assert normalize_date("08.08.26") == "08.08.26"