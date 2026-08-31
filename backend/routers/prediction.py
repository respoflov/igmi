from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

import os
import uuid
import shutil

from database.database import get_db
from models.prediction import Prediction

from services.yolo_service import yolo_service

from config import UPLOAD_DIR


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


@router.post("/")
async def predict_banana(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # 확장자 확인
    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="이미지 파일만 업로드할 수 있습니다."
        )


    # UUID 파일명 생성
    filename = (
        f"{uuid.uuid4().hex}{extension}"
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )


    # 파일 저장
    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    try:

        # YOLO 추론
        result = yolo_service.predict(
            file_path
        )


        # PostgreSQL 저장
        prediction = Prediction(

            original_filename=file.filename,

            image_path=(
                f"storage/uploads/{filename}"
            ),

            result_image_path=(
                result["result_image_path"]
            ),

            predicted_class=(
                result["predicted_class"]
            ),

            confidence=(
                result["confidence"]
            )
        )


        db.add(
            prediction
        )

        db.commit()

        db.refresh(
            prediction
        )


        return {

            "success": True,

            "prediction_id":
                prediction.id,

            "predicted_class":
                result["predicted_class"],

            "confidence":
                result["confidence"],

            "detections":
                result["detections"],

            "image_path":
                prediction.image_path,

            "result_image_path":
                prediction.result_image_path
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )