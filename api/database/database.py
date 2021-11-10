import asyncio

from api import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from api.database.models import Base

# create database engine

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

engine = create_async_engine(Config.sql_uri, poolclass=NullPool, echo=True, echo_pool=True)
discord_engine = create_async_engine(Config.discord_sql_uri, poolclass=NullPool)

asyncio.gather(async_main())

async_session = sessionmaker(engine, class_= AsyncSession, expire_on_commit=False, autoflush=True)
async_discord_session = sessionmaker(discord_engine, class_= AsyncSession, expire_on_commit=False)
