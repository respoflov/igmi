from sqlalchemy.orm import Session
from sqlalchemy import func

from models.banana_fact import BananaFact


def get_random_facts_by_chars(db: Session, max_chars: int = 50, pool_size: int = 30):

    rows = (
        db.query(BananaFact)
        .order_by(func.random())
        .limit(pool_size)
        .all()
    )

    result = []
    total = 0

    for row in rows:

        content = row.content
        added_len = len(content) if not result else len(content) + 1

        if total + added_len <= max_chars:

            result.append(content)
            total += added_len

    if not result and rows:
        result.append(rows[0].content)

    return result
