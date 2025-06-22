from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0}
)
print("✅ Engine created with statement_cache_size=0")


# Async session factory
async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Create tables asynchronously
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# Async generator for dependency injection
async def get_session():
    async with async_session_maker() as session:
        yield session
