from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.future import select
from db import Base, session
from hashlib import sha256

class Person(Base):
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, autoincrement=False)
    account_id = mapped_column(ForeignKey("account.id", ondelete='CASCADE', onupdate="CASCADE"))
    snils_hash = Column(String)
    born_hash = Column(String)
    passport_hash = Column(String)
    account = relationship("Account", back_populates="person", lazy="selectin", foreign_keys=[account_id])

    def __init__(self, person_id, fist_name, last_name):
        self.id = person_id
        self.first_name = fist_name
        self.last_name = last_name

    def add_snils(self, snils):
        self.snils_hash = sha256(f"{self.first_name}+{self.last_name}+{snils}".encode()).hexdigest()

    def add_born(self, born):
        self.born_hash = sha256(f"{self.first_name}+{self.last_name}+{born}".encode()).hexdigest()

    def add_passport(self, passport):
        self.passport_hash = sha256(f"{self.first_name}+{self.last_name}+{passport}".encode()).hexdigest()

    async def create(self):
        db_session = await session()
        db_session.add(self)
        await db_session.commit()
        await db_session.close()
        return self
    
    async def set_account_id(id, account_id):
        db_session = await session()
        person = (await (db_session.scalars(select(Person).where(Person.id == id)))).one_or_none()
        person.account_id = account_id
        await db_session.commit()
        await db_session.close()

    @staticmethod
    async def get_person_by_id(id):
        db_session = await session()
        person = (await (db_session.scalars(select(Person).where(Person.id == id)))).one_or_none()
        await db_session.close()
        return person

    @staticmethod
    async def __get_person_by_snils(first_name, last_name, snils):
        db_session = await session()
        person = (await db_session.scalars(select(Person).where(Person.snils_hash == sha256(f"{first_name}+{last_name}+{snils}".encode()).hexdigest()))).one_or_none()
        await db_session.close()
        return person
    
    @staticmethod
    async def __get_person_by_born(first_name, last_name, born):
        db_session = await session()
        person = (await db_session.scalars(select(Person).where(Person.born_hash == sha256(f"{first_name}+{last_name}+{born}".encode()).hexdigest()))).one_or_none()
        await db_session.close()
        return person
    
    @staticmethod
    async def __get_person_by_passport(first_name, last_name, passport):
        db_session = await session()
        person = (await db_session.scalars(select(Person).where(Person.passport_hash == sha256(f"{first_name}+{last_name}+{passport}".encode()).hexdigest()))).one_or_none()
        await db_session.close()
        return person

    async def get_id_by_snils(first_name, last_name, snils):
        if person := await Person.__get_person_by_snils(first_name, last_name, snils):
            return person.id
        return False
                
    async def get_id_by_born(first_name, last_name, born):
        if person := await Person.__get_person_by_born(first_name, last_name, born):
            return person.id
        return False
    
    async def get_id_by_passport(first_name, last_name, passport):
        if person := await Person.__get_person_by_passport(first_name, last_name, passport):
            return person.id
        return False
    
    async def is_authenticated_by_snils(first_name, last_name, snils):
        if person := await Person.__get_person_by_snils(first_name, last_name, snils):
            return person.account_id
        return False
                
    async def is_authenticated_by_born(first_name, last_name, born):
        if person := await Person.__get_person_by_born(first_name, last_name, born):
            return person.account_id
        return False

    async def is_authenticated_by_passport(first_name, last_name, passport):
        if person := await Person.__get_person_by_passport(first_name, last_name, passport):
            return person.account_id
        return False
