from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os


Base = declarative_base()

# pytest 專用，完全使用記憶體
TESTING = os.getenv("TESTING") == "1"

if TESTING:
    # 不產生任何檔案，不會污染 news_database.db 或 test.db
    DATABASE_URL = "sqlite:///:memory:"
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'news_database.db')}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
