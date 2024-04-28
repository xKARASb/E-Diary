from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = "db.sqlite"
engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_NAME}", echo=False)
Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def session():
    return Session()

Base = declarative_base()

async def create_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)