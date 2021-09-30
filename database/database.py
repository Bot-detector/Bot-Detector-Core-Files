import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# create database engine
engine = create_async_engine(Config.sql_uri, poolclass=NullPool)
discord_engine = create_async_engine(Config.discord_sql_uri, poolclass=NullPool)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_discord_session = sessionmaker(discord_engine, class_=AsyncSession, expire_on_commit=False)


