from db import Base, session
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.future import select


class Account(Base):
    __tablename__ = 'account'
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    learner: Mapped["Learner"] = relationship(back_populates="account", lazy="selectin", uselist=False)

    def __init__(self, id):
        self.id = id

    async def get_account(self):
        db_session = await session()
        result = (await db_session.scalars(select(Account).filter(Account.id == self.id))).one_or_none()
        await db_session.close()
        return result