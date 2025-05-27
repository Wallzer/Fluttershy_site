# database.py

from sqlalchemy import create_engine,event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
import sqlite3
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./test.db"  # или твой URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Вот ЭТА функция нужна для Depends(get_db)
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@event.listens_for(Engine, "connect")
def _fk_pragma_on_connect(dbapi_con, connection_record):
    if isinstance(dbapi_con, sqlite3.Connection):
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()