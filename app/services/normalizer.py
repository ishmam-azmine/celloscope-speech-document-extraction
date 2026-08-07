import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedValue:
    value: float
    qualifier: str | None = None
    raw_value: str | None = None


def normalize_numeric_value(value: str) -> float | None:
    result = parse_numeric_value(value)
    return result.value if result else None


def parse_numeric_value(value: str) -> NormalizedValue | None:
    raw_value = value.strip()
    cleaned = raw_value.replace(",", "")

    qualifier = None

    qualifier_match = re.match(r"^(<=|>=|<|>|≤|≥)\s*", cleaned)
    if qualifier_match:
        qualifier = qualifier_match.group(1)
        cleaned = cleaned[qualifier_match.end():].strip()

    scientific_match = re.fullmatch(
        r"([+-]?\d+(?:\.\d+)?)\s*[x×]\s*10\s*\^?\s*([+-]?\d+)",
        cleaned,
        flags=re.IGNORECASE,
    )

    if scientific_match:
        coefficient = float(scientific_match.group(1))
        exponent = int(scientific_match.group(2))

        return NormalizedValue(
            value=coefficient * (10 ** exponent),
            qualifier=qualifier,
            raw_value=raw_value,
        )

    try:
        return NormalizedValue(
            value=float(cleaned),
            qualifier=qualifier,
            raw_value=raw_value,
        )
    except ValueError:
        return None


def normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None

    cleaned = unit.strip()

    aliases = {
        "gm/dl": "g/dL",
        "g/dl": "g/dL",
        "mg/dl": "mg/dL",
        "mmol/l": "mmol/L",
        "meq/l": "mEq/L",
        "iu/l": "IU/L",
        "u/l": "U/L",
        "10^3/ul": "10^3/µL",
        "10^3/μl": "10^3/µL",
        "10^3/µl": "10^3/µL",
        "10³/ul": "10^3/µL",
        "10³/μl": "10^3/µL",
        "10³/µl": "10^3/µL",
    }

    return aliases.get(cleaned.lower(), cleaned)


def normalize_reference_range(reference_range: str | None) -> str | None:
    if reference_range is None:
        return None

    cleaned = reference_range.strip()

    cleaned = re.sub(
        r"\s*(?:-|–|—|to)\s*",
        "-",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned or None