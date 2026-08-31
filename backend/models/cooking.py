from sqlalchemy import Column, Integer, String, Text

from database.database import Base


class Cooking(Base):

    __tablename__ = "cooking"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ripeness_class = Column(
        String,
        nullable=False,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )
