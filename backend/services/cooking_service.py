from sqlalchemy.orm import Session

from models.cooking import Cooking


def list_cooking(db: Session):

    rows = (
        db.query(Cooking)
        .order_by(Cooking.id)
        .all()
    )

    grouped = {}

    for row in rows:

        grouped.setdefault(row.ripeness_class, []).append(
            {
                "title": row.title,
                "description": row.description,
            }
        )

    return grouped


def get_cooking(db: Session, ripeness_class: str):

    rows = (
        db.query(Cooking)
        .filter(Cooking.ripeness_class == ripeness_class)
        .order_by(Cooking.id)
        .all()
    )

    if not rows:
        return None

    return [
        {
            "title": row.title,
            "description": row.description,
        }
        for row in rows
    ]
