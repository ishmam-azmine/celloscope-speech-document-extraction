from app.services.normalizer import normalize_numeric_value, normalize_unit


def test_normalizes_decimal():
    assert normalize_numeric_value("12.5") == 12.5


def test_normalizes_comma_separated_number():
    assert normalize_numeric_value("12,500") == 12500.0


def test_normalizes_less_than_value():
    assert normalize_numeric_value("<0.5") == 0.5


def test_normalizes_scientific_notation():
    assert normalize_numeric_value("1.2 × 10^3") == 1200.0


def test_invalid_value_returns_none():
    assert normalize_numeric_value("not-a-number") is None


def test_normalizes_common_units():
    assert normalize_unit("gm/dl") == "g/dL"
    assert normalize_unit("mg/dl") == "mg/dL"
    assert normalize_unit("mmol/l") == "mmol/L"
    assert normalize_unit("10^3/uL") == "10^3/µL"