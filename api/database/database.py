from asyncio.tasks import current_task
from enum import Enum, auto

from sqlalchemy.ext.asyncio.engine import AsyncConnection, AsyncEngine

from api import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


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

        self.engine = create_async_engine(
            connection_string, 
            poolclass=QueuePool,
            pool_pre_ping=True

        )
        self.session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def get_engine(self) -> AsyncEngine:
        return self.engine
    
    def get_connection(self) -> AsyncConnection:
        return self.engine.connect()
        
    def get_sessionmaker(self) -> sessionmaker:
        return self.session
    
    def get_scoped_session(self) -> async_scoped_session:
        return async_scoped_session(self.session, scopefunc=current_task)

playerdata = Engine(EngineType.PLAYERDATA)
discord = Engine(EngineType.DISCORD)

playerdata_engine = create_async_engine(
    Config.sql_uri, 
    poolclass=QueuePool, 
    pool_size=10, 
    max_overflow=100,
    pool_recycle=50,
    echo="debug"
)
discord_engine = create_async_engine(
    Config.discord_sql_uri, 
    poolclass=QueuePool, 
    pool_size=10, 
    max_overflow=100,
    pool_recycle=50
)
def get_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=True)