from sqlalchemy import Column, Integer, String, Text

from database.database import Base


class BananaRiping(Base):

    __tablename__ = "banana_riping"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    humidity_key = Column(
        String,
        nullable=False,
        unique=True
    )

    humidity_label = Column(
        String,
        nullable=False
    )

    temp_under_10 = Column(Text, nullable=True)
    temp_13_15 = Column(Text, nullable=True)
    temp_18_20 = Column(Text, nullable=True)
    temp_25_30 = Column(Text, nullable=True)
    temp_over_35 = Column(Text, nullable=True)
