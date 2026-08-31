from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database.database import get_db

from services import ripening_service


router = APIRouter(
    prefix="/ripening",
    tags=["Ripening"]
)


# 습도 / 온도 선택지 조회
@router.get("/options")
def get_ripening_options(
    db: Session = Depends(get_db)
):

    return ripening_service.list_options(db)


# 보관 조건(습도/온도)에 따른 후숙 예상 기간 조회
@router.get("/estimate")
def get_ripening_estimate(
    humidity_key: str,
    temp_key: str,
    db: Session = Depends(get_db)
):

    result = ripening_service.estimate_ripening_days(
        db,
        humidity_key,
        temp_key
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="해당 보관 조건에 대한 데이터를 찾을 수 없습니다."
        )

    return result
