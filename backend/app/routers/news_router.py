from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.news_schema import News, NewsCreate
from app.services.news_service import NewsService

router = APIRouter()
news_service = NewsService()

# 取得所有新聞
@router.get("/", response_model=list[News])
def get_all_news(db: Session = Depends(get_db)):
    return news_service.get_news_list(db)

# 新增新聞
@router.post("/", response_model=News)
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    return news_service.create_news(db, news)

# 刪除新聞
@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    return news_service.delete_news(db, news_id)

# 爬蟲功能
@router.get("/crawl", response_model=list[dict])
def crawl_news():
    """爬取最新 Hacker News"""
    return news_service.crawl_latest_news()

