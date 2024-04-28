from db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column


class Account(Base):
    __tablename__ = 'account'
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    learner_id = Column(ForeignKey('learner.id'), unique=True)

