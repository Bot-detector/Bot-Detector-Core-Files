from sqlalchemy import Column, DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'Players'

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime) # DEFAULT CURRENT_TIMESTAMP
    updated_at = Column(DateTime)
    possible_ban = Column(SmallInteger, default=0)
    confirmed_ban = Column(SmallInteger, default=0)
    confirmed_player = Column(SmallInteger, default=0)
    label_id = Column(Integer, default=0)
    label_jagex = Column(Integer, default=0)

    # relationships

class Label(Base):
    __tablename__ = 'Labels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String)

