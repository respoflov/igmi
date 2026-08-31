from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    original_filename = Column(
        String,
        nullable=False
    )

    image_path = Column(
        String,
        nullable=False
    )

    result_image_path = Column(
        String,
        nullable=True
    )

    predicted_class = Column(
        String,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )