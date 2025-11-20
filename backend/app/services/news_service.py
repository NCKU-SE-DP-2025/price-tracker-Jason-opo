import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.news import News
from app.schemas.news_schema import NewsCreate


class NewsService:
    """新聞管理與爬蟲邏輯"""

    def get_news_list(self, db: Session):
        return db.query(News).order_by(News.id.desc()).all()

    def create_news(self, db: Session, news: NewsCreate):
        # 檢查是否已有相同 URL
        existing = db.query(News).filter(News.url == news.url).first()
        if existing:
            raise HTTPException(status_code=400, detail="News already exists")

        db_news = News(
            title=news.title,
            url=news.url,
            time=news.time,
            content=news.content,
            summary=news.summary,
            reason=news.reason
        )
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news

    def delete_news(self, db: Session, news_id: int):
        db_news = db.query(News).filter(News.id == news_id).first()
        if not db_news:
            raise HTTPException(status_code=404, detail="News not found")
        db.delete(db_news)
        db.commit()
        return {"message": "News deleted successfully"}

    def crawl_latest_news(self):
        """簡易爬 Hacker News 的新聞"""
        url = "https://news.ycombinator.com/"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch news data")

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for item in soup.select(".athing"):
            title_tag = item.select_one(".titleline a")
            if title_tag:
                results.append({
                    "title": title_tag.text.strip(),
                    "url": title_tag["href"],
                    "time": "N/A",      # 可之後再補實際時間
                    "content": "",
                    "summary": "",
                    "reason": ""
                })
        return results
