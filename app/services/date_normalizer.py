from datetime import datetime


WRITTEN_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d %B %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%b %d, %Y",
)


def normalize_date(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    for date_format in WRITTEN_DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, date_format)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    numeric = _normalize_numeric_date(cleaned)

    if numeric is not None:
        return numeric

    return cleaned


def _normalize_numeric_date(value: str) -> str | None:
    separator = None

    if "/" in value:
        separator = "/"
    elif "-" in value:
        separator = "-"

    if separator is None:
        return None

    parts = value.split(separator)

    if len(parts) != 3:
        return None

    first, second, year = parts

    if not (
        first.isdigit()
        and second.isdigit()
        and year.isdigit()
        and len(year) == 4
    ):
        return None

    first_number = int(first)
    second_number = int(second)

    if first_number > 12 and second_number <= 12:
        date_format = f"%d{separator}%m{separator}%Y"
    elif second_number > 12 and first_number <= 12:
        date_format = f"%m{separator}%d{separator}%Y"
    else:
        return None

    try:
        parsed = datetime.strptime(value, date_format)
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None