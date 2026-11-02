from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///nexus_sync.db")

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Memory(Base):
    __tablename__ = "memory"

    id = Column(String, primary_key=True)
    content = Column(Text)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True)
    content = Column(Text)


def init_db():
    Base.metadata.create_all(engine)
