import re

from sqlalchemy.orm import Session

from models.banana_riping import BananaRiping


TEMP_OPTIONS = {
    "under_10": {
        "column": "temp_under_10",
        "label": "10°C 이하",
    },
    "13_15": {
        "column": "temp_13_15",
        "label": "13°C ~ 15°C (최적)",
    },
    "18_20": {
        "column": "temp_18_20",
        "label": "18°C ~ 20°C (실온)",
    },
    "25_30": {
        "column": "temp_25_30",
        "label": "25°C ~ 30°C",
    },
    "over_35": {
        "column": "temp_over_35",
        "label": "35°C 이상",
    },
}

DAYS_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:[~\-]\s*(\d+(?:\.\d+)?))?\s*일"
)


def parse_days(cell_text: str):

    if not cell_text:
        return None, None, None

    lines = str(cell_text).splitlines()

    days_part = lines[0].strip()

    note = " ".join(
        line.strip().lstrip("• ").strip()
        for line in lines[1:]
        if line.strip()
    ) or None

    match = DAYS_PATTERN.search(days_part)

    if not match:
        return None, None, note

    min_days = float(match.group(1))

    max_days = (
        float(match.group(2))
        if match.group(2)
        else min_days
    )

    return min_days, max_days, note


def list_options(db: Session):

    rows = (
        db.query(
            BananaRiping.humidity_key,
            BananaRiping.humidity_label
        )
        .order_by(BananaRiping.id)
        .all()
    )

    return {
        "humidity_options": [
            {"key": key, "label": label}
            for key, label in rows
        ],
        "temp_options": [
            {"key": key, "label": v["label"]}
            for key, v in TEMP_OPTIONS.items()
        ],
    }


def estimate_ripening_days(
    db: Session,
    humidity_key: str,
    temp_key: str
):

    temp_info = TEMP_OPTIONS.get(temp_key)

    if temp_info is None:
        return None

    row = (
        db.query(BananaRiping)
        .filter(BananaRiping.humidity_key == humidity_key)
        .first()
    )

    if row is None:
        return None

    cell_text = getattr(row, temp_info["column"])

    min_days, max_days, note = parse_days(cell_text)

    return {
        "humidity_key": row.humidity_key,
        "humidity_label": row.humidity_label,
        "temp_key": temp_key,
        "temp_label": temp_info["label"],
        "min_days": min_days,
        "max_days": max_days,
        "note": note,
        "raw_text": cell_text,
    }
