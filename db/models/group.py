from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from db import Base


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    course: Mapped[int] = mapped_column(Integer)
    liter: Mapped[str] = mapped_column(String)
    learner = relationship("Learner", back_populates="group", lazy="selectin")


    def __init__(self, id, course, liter):
        self.id = id
        self.course = course
        self.liter = liter