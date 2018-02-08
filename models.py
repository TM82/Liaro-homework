from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

class Content(Base):
    __tablename__ = 'contents'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, nullable = False)
    to_id = Column(Integer, nullable = False)
    content = Column(String(255), nullable = False)
    datetime = Column(DateTime, nullable = False)
