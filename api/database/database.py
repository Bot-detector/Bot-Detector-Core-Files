from enum import Enum, auto
from typing import AsyncGenerator

from api import Config
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


class EngineType(Enum):
    PLAYERDATA = auto()
    DISCORD = auto()


class Engine():
    def __init__(self, engine_type: EngineType = EngineType.PLAYERDATA):
        self.type = engine_type
        
        if self.type == EngineType.PLAYERDATA:
            connection_string = Config.sql_uri
        elif self.type == EngineType.DISCORD:
            connection_string = Config.discord_sql_uri
        else:
            raise ValueError(f"Engine type {engine_type} not valid.")

        self.engine = create_async_engine(
            connection_string, poolclass=QueuePool,
            pool_size=100, max_overflow=10, 
            pool_recycle=900, pool_timeout=60
        )
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=True)


"""Our Database Engines"""
PLAYERDATA_ENGINE = Engine(EngineType.PLAYERDATA)
DISCORD_ENGINE = Engine(EngineType.DISCORD)


async def get_engine(type: EngineType):
    """Returns a COPY of a globally defined database engine. Don't use the returned copy for actual transactions."""
    if type == EngineType.PLAYERDATA:
        return PLAYERDATA_ENGINE.engine
    elif type == EngineType.DISCORD:
        return DISCORD_ENGINE.engine
    else:
        raise ValueError(f"Engine type {type} not valid.")


@asynccontextmanager
async def get_session(type: EngineType) -> AsyncGenerator[AsyncSession, None]:
    """Provides an AsyncGenerator to allow creation of a database session."""
    if type == EngineType.PLAYERDATA:
        async with PLAYERDATA_ENGINE.session() as session:
            yield session
    elif type == EngineType.DISCORD:
        async with DISCORD_ENGINE.session() as session:
            yield session
    else:
        raise ValueError(f"Engine type {type} not valid.")