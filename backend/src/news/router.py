from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from src.news.service import get_article_upvote_details, toggle_upvote
from src.news.service import NewsService
from src.news.ai_service import AIService
from src.news.models import NewsArticle
from src.news.schemas import PromptRequest, NewsSummaryRequest
from src.auth.router import get_current_user
from src.core.database import get_db  # ✅ 正確的 DB session 依賴

router = APIRouter()
ai_service = AIService()
news_service = NewsService(ai_service)


# 搜尋新聞：POST /api/v1/news/search_news
@router.post("/search_news")
def search_news(req: PromptRequest):
    keywords = ai_service.extract_keywords(req.prompt)
    return news_service.get_news_info(keywords)


# 新聞摘要：POST /api/v1/news/news_summary
@router.post("/news_summary")
def summarize_news(req: NewsSummaryRequest, user=Depends(get_current_user)):
    return ai_service.summarize(req.content)


# 讀取所有新聞：GET /api/v1/news/news
@router.get("/news")
def read_news(db: Session = Depends(get_db)):
    """
    取得所有新聞，依照時間新到舊排序。
    """
    news_list = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    print(news_list)
    for article in news_list:
        # 尚未登入的使用者不需要投票狀態
        upvotes, is_upvoted = get_article_upvote_details(article.id, None, db)
        result.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
        )
    return result


# 讀取使用者新聞：GET /api/v1/news/user_news
@router.get("/user_news")
def read_user_news(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    取得使用者新聞（含是否投過票）。
    """
    news_list = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news_list:
        upvotes, is_upvoted = get_article_upvote_details(article.id, user.id, db)
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "time": article.time,
            "summary": article.summary,
            "reason": article.reason,
            "upvotes": upvotes,
            "is_upvoted": is_upvoted
        })
    return result

@router.post("/{id}/upvote")
def upvote_article(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    message = toggle_upvote(id, user.id, db)
    return {"message": message}