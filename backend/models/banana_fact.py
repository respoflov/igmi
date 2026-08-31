from sqlalchemy import Column, Integer, Text

from database.database import Base


class BananaFact(Base):

    __tablename__ = "banana_fact"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    content = Column(
        Text,
        nullable=False
    )
