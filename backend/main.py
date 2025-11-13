from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import Base, engine
from src.core.scheduler import start_scheduler, stop_scheduler
from src.auth.router import router as auth_router
from src.news.router import router as news_router
from src.prices.router import router as prices_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/users", tags=["users"])
app.include_router(news_router, prefix="/api/v1/news", tags=["news"])
app.include_router(prices_router, prefix="/api/v1/prices", tags=["prices"])

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


'''
import json
import itertools
import os
from datetime import datetime, timedelta
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import sentry_sdk

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt
from passlib.context import CryptContext
from openai import OpenAI
from pydantic import BaseModel

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Table,
    create_engine, select, insert, delete
)
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base

# -------------------------------
# 基礎設定
# -------------------------------
Base = declarative_base()
engine = create_engine("sqlite:///news_database.db", echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

sentry_sdk.init(
    dsn="https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# -------------------------------
# 資料表定義
# -------------------------------
user_news_association_table = Table(
    "user_news_upvotes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("news_articles_id", Integer, ForeignKey("news_articles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    upvoted_news = relationship(
        "NewsArticle", secondary=user_news_association_table, back_populates="upvoted_by_users"
    )


class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    time = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    upvoted_by_users = relationship(
        "User", secondary=user_news_association_table, back_populates="upvoted_news"
    )


Base.metadata.create_all(engine)

# -------------------------------
# 工具類別：資料庫操作
# -------------------------------
class DatabaseManager:
    def __init__(self):
        self.SessionLocal = SessionLocal

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# -------------------------------
# 工具類別：AI 助手
# -------------------------------
class AIService:
    def __init__(self, api_key="xxx"):
        self.client = OpenAI(api_key=api_key)

    def summarize(self, content: str):
        messages = [
            {"role": "system", "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})"},
            {"role": "user", "content": content},
        ]
        result = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        return json.loads(result.choices[0].message.content)

    def extract_keywords(self, prompt: str):
        messages = [
            {"role": "system", "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取最重要的關鍵字即可。"},
            {"role": "user", "content": prompt},
        ]
        result = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        return result.choices[0].message.content.strip()


# -------------------------------
# 服務層：使用者認證與登入
# -------------------------------
class AuthService:
    SECRET_KEY = "1892dhianiandowqd0n"
    ALGORITHM = "HS256"

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return password_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password):
        return password_context.hash(password)

    @staticmethod
    def create_access_token(data, expires_delta=None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM)

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])


# -------------------------------
# 服務層：新聞管理
# -------------------------------
class NewsService:
    def __init__(self, ai_service: AIService):
        self.ai = ai_service

    def get_news_info(self, keyword, is_initial=False):
        url = "https://udn.com/api/more"
        if is_initial:
            all_pages = []
            for i in range(1, 10):
                params = {"page": i, "id": f"search:{quote(keyword)}", "channelId": 2, "type": "searchword"}
                all_pages.extend(requests.get(url, params=params).json()["lists"])
            return all_pages
        else:
            params = {"page": 1, "id": f"search:{quote(keyword)}", "channelId": 2, "type": "searchword"}
            return requests.get(url, params=params).json()["lists"]

    def add_news(self, db: Session, data):
        article = NewsArticle(**data)
        db.add(article)
        db.commit()
        db.close()

    def crawl_and_save_news(self, db: Session):
        keyword = "價格"
        news_data = self.get_news_info(keyword)
        for news in news_data:
            try:
                soup = BeautifulSoup(requests.get(news["titleLink"]).text, "html.parser")
                title = soup.find("h1", class_="article-content__title").text
                time = soup.find("time", class_="article-content__time").text
                content_section = soup.find("section", class_="article-content__editor")
                paragraphs = [p.text for p in content_section.find_all("p") if p.text.strip()]
                result = self.ai.summarize(" ".join(paragraphs))
                data = {
                    "url": news["titleLink"], "title": title, "time": time,
                    "content": " ".join(paragraphs),
                    "summary": result["影響"], "reason": result["原因"]
                }
                self.add_news(db, data)
            except Exception as e:
                print("Error parsing:", e)


# -------------------------------
# FastAPI 初始化
# -------------------------------
app = FastAPI(title="OOP Refactored News API")
bgs = BackgroundScheduler()
ai_service = AIService()
news_service = NewsService(ai_service)
db_manager = DatabaseManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    db = next(db_manager.get_db())
    if db.query(NewsArticle).count() == 0:
        news_service.crawl_and_save_news(db)
    db.close()
    bgs.add_job(lambda: news_service.crawl_and_save_news(next(db_manager.get_db())), "interval", minutes=100)
    bgs.start()


@app.on_event("shutdown")
def shutdown_event():
    bgs.shutdown()


# -------------------------------
# Schema 定義
# -------------------------------
class UserAuthSchema(BaseModel):
    username: str
    password: str


class PromptRequest(BaseModel):
    prompt: str


class NewsSummaryRequest(BaseModel):
    content: str


# -------------------------------
# API 區塊
# -------------------------------
@app.post("/api/v1/users/register")
def register_user(user: UserAuthSchema, db: Session = Depends(db_manager.get_db)):
    hashed_pw = AuthService.hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


@app.post("/api/v1/users/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_manager.get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = AuthService.create_access_token({"sub": user.username}, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_manager.get_db)):
    payload = AuthService.decode_token(token)
    username = payload.get("sub")
    return db.query(User).filter(User.username == username).first()


@app.get("/api/v1/users/me")
def get_me(user=Depends(get_current_user)):
    return {"username": user.username}


@app.post("/api/v1/news/search_news")
def search_news(req: PromptRequest):
    keywords = ai_service.extract_keywords(req.prompt)
    results = news_service.get_news_info(keywords)
    return results


@app.post("/api/v1/news/news_summary")
def summarize_news(req: NewsSummaryRequest, user=Depends(get_current_user)):
    return ai_service.summarize(req.content)


@app.get("/api/v1/prices/necessities-price")
def get_necessities_prices(category=Query(None), commodity=Query(None)):
    url = "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice"
    return requests.get(url, params={"CategoryName": category, "Name": commodity}).json()
'''