from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from .config import settings

engine = create_engine(settings.db_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    actor = Column(String(64))
    action = Column(String(128))
    payload = Column(JSON)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(64), unique=True, index=True)
    name = Column(String(128))
    email = Column(String(128))
    phone = Column(String(64))

def init_db():
    Base.metadata.create_all(bind=engine)
