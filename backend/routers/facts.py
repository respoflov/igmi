from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from database.database import get_db

from services import fact_service


router = APIRouter(
    prefix="/facts",
    tags=["Facts"]
)


# 바나나 상식 랜덤 조회 (글자 수 기준으로 채워서 반환)
@router.get("/random")
def get_random_facts(
    max_chars: int = Query(50, ge=10, le=500),
    db: Session = Depends(get_db)
):

    return {
        "facts": fact_service.get_random_facts_by_chars(db, max_chars)
    }
