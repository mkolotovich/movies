from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Movie(DeclarativeBase):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    description = Column('description', String)
    rating = Column('rating', Float)
