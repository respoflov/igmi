from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database.database import get_db

from services import cooking_service


router = APIRouter(
    prefix="/cooking",
    tags=["Cooking"]
)


# 숙성도별 조리 · 섭취 방법 전체 조회
@router.get("/")
def get_cooking_list(
    db: Session = Depends(get_db)
):

    return cooking_service.list_cooking(db)


# 특정 숙성도의 조리 · 섭취 방법 조회
@router.get("/{ripeness_class}")
def get_cooking_by_class(
    ripeness_class: str,
    db: Session = Depends(get_db)
):

    result = cooking_service.get_cooking(
        db,
        ripeness_class
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="해당 숙성도에 대한 조리 방법을 찾을 수 없습니다."
        )

    return result
