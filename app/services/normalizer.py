import re


def normalize_numeric_value(value: str) -> float | None:
    cleaned = value.strip().replace(",", "")

    if cleaned.startswith(("<", ">", "≤", "≥")):
        cleaned = cleaned[1:].strip()

    scientific_match = re.fullmatch(
        r"([+-]?\d+(?:\.\d+)?)\s*[x×]\s*10\^?([+-]?\d+)",
        cleaned,
        flags=re.IGNORECASE,
    )

    if scientific_match:
        coefficient = float(scientific_match.group(1))
        exponent = int(scientific_match.group(2))
        return coefficient * (10 ** exponent)

    try:
        return float(cleaned)
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
        "10^3/ul": "10^3/µL",
        "10^3/μl": "10^3/µL",
        "10^3/µl": "10^3/µL",
    }

    return aliases.get(cleaned.lower(), cleaned)