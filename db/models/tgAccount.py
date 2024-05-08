from db import Base, session
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.future import select


class Account(Base):
    __tablename__ = 'account'
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    first_name = Column(String)
    person: Mapped["Person"] = relationship(back_populates="account", lazy="selectin", uselist=False)

    def __init__(self, id, first_name=None):
        self.id = id
        self.first_name = first_name

    async def create(self):
        db_session = await session()
        if self.first_name:
            db_session.add(self)
            await db_session.commit()
            await db_session.close()
            return self
        else:
            await db_session.close()
            raise ValueError("Account must have a first name")

    async def get_account(self):
        db_session = await session()
        result = (await db_session.scalars(select(Account).filter(Account.id == self.id))).one_or_none()
        await db_session.close()
        return result
    
    async def get_all():
        db_session = await session()
        result = (await db_session.scalars(select(Account))).all()
        await db_session.close()
        return result
