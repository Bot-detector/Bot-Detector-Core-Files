from enum import Enum, auto

from api import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from asyncio import current_task
from sqlalchemy.ext.asyncio import async_scoped_session

class EngineType(Enum):
    """"""
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

        self.engine = create_async_engine(connection_string, poolclass=QueuePool, pool_size=100)
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        # self.session = async_scoped_session(self.session_maker, scopefunc=current_task)

