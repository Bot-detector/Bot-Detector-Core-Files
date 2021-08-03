import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# create databas engine
engine = create_async_engine(Config.sql_uri, poolclass=NullPool)
discord_engine = create_async_engine(Config.discord_sql_uri, poolclass=NullPool)
