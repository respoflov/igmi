from ultralytics import YOLO
from pathlib import Path
import uuid

from config import MODEL_PATH, RESULT_DIR


class YOLOService:

    def __init__(self):

        print("YOLO 모델 로딩 중...")

        self.model = YOLO(MODEL_PATH)

        print("YOLO 모델 로딩 완료")


    def predict(self, image_path):

        results = self.model(
            image_path
        )

        result = results[0]

        names = result.names


        # 탐지 결과가 없는 경우
        if result.boxes is None or len(result.boxes) == 0:

            return {
                "predicted_class": "unknown",
                "confidence": 0.0,
                "result_image_path": None,
                "detections": []
            }


        detections = []


        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            confidence = float(
                box.conf[0]
            )

            class_name = names[
                class_id
            ]

            detections.append(
                {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence
                }
            )


        # confidence가 가장 높은 결과
        best_detection = max(
            detections,
            key=lambda x: x["confidence"]
        )


        # 결과 이미지 저장
        result_filename = (
            f"{uuid.uuid4().hex}.jpg"
        )

        result_path = Path(
            RESULT_DIR
        ) / result_filename


        result.save(
            filename=str(result_path)
        )


        return {
            "predicted_class": best_detection[
                "class_name"
            ],

            "confidence": best_detection[
                "confidence"
            ],

            "result_image_path":
                f"storage/results/{result_filename}",

            "detections": detections
        }


yolo_service = YOLOService()