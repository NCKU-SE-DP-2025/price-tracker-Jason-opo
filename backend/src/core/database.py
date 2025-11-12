from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 讓 BASE_DIR 指向 backend 目錄
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'news_database.db')}"

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
