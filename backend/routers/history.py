from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

import os

from database.database import get_db

from models.prediction import Prediction


router = APIRouter(
    prefix="/history",
    tags=["History"]
)


# 전체 기록 조회
@router.get("/")
def get_history(
    db: Session = Depends(get_db)
):

    predictions = (
        db.query(Prediction)
        .order_by(
            Prediction.created_at.desc()
        )
        .all()
    )


    return predictions


# 특정 기록 조회
@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.id == prediction_id
        )
        .first()
    )


    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="기록을 찾을 수 없습니다."
        )


    return prediction


# 기록 삭제
@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.id == prediction_id
        )
        .first()
    )


    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="기록을 찾을 수 없습니다."
        )


    # 실제 파일 경로
    backend_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


    if prediction.image_path:

        image_path = os.path.join(
            backend_dir,
            prediction.image_path
        )


        if os.path.exists(image_path):

            os.remove(
                image_path
            )


    if prediction.result_image_path:

        result_path = os.path.join(
            backend_dir,
            prediction.result_image_path
        )


        if os.path.exists(result_path):

            os.remove(
                result_path
            )


    db.delete(
        prediction
    )

    db.commit()


    return {
        "success": True,
        "message": "분석 기록이 삭제되었습니다."
    }