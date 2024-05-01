from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.future import select
from db import Base


class Learner(Base):
    __tablename__ = "learner"


    id = Column(Integer, primary_key=True, autoincrement=False)
    person_id = Column(Integer, unique=True)
    account_id = mapped_column(ForeignKey("account.id", ondelete='CASCADE', onupdate="CASCADE"))
    group_id = mapped_column(ForeignKey("group.id"))
    first_name = Column(String)
    last_name = Column(String)
    birthday = Column(Date)

    group: Mapped["Group"] = relationship(back_populates="learner", lazy="selectin", foreign_keys=[group_id])
    account = relationship("Account", back_populates="learner", lazy="selectin", foreign_keys=[account_id])

    def __init__(self, id=None, group_id=None, first_name=None, last_name=None, birthday=None):
        self.id = id
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday

    async def get_learner_by_name(session, first_name = None, last_name = None):
        return (await session.execute(select(Learner).where((Learner.first_name == first_name) & (Learner.last_name == last_name)))).scalars()
        # return (await session.scalars(select(Learner).filter((Learner.first_name == first_name) & (Learner.last_name == last_name)))).all()