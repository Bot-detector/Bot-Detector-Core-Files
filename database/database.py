import Config
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# create databas engine
engine = create_engine(Config.sql_uri, poolclass=NullPool)
discord_engine = create_engine(Config.discord_sql_uri, poolclass=NullPool)
