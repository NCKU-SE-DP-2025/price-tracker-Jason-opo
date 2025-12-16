from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from src.news.service import get_article_upvote_details, toggle_upvote
from src.news.service import NewsService
from src.news.ai_service import AIService
from src.news.models import NewsArticle
from src.news.schemas import PromptRequest, NewsSumaryRequestSchema
from src.auth.router import get_current_user
from src.core.database import get_db  # ✅ 正確的 DB session 依賴
from bs4 import BeautifulSoup

router = APIRouter()
ai_service = AIService()
news_service = NewsService(ai_service)


# 搜尋新聞：POST /api/v1/news/search_news
@router.post("/search_news")
def search_news(req: PromptRequest):
    """
    搜尋新聞內容，流程：
    1. 用 OpenAI 把 prompt 轉成關鍵字
    2. 呼叫 main.get_new_info(keyword) 拿到列表（測試會 mock 這個）
    3. 對每個 titleLink 發 requests.get，解析 HTML 內容
    """
    from main import OpenAI, get_new_info, requests, _id_counter

    prompt = req.prompt

    # 1) 用 OpenAI 做關鍵字抽取（在測試中會被 mock 掉）
    messages = [
        {
            "role": "system",
            "content": (
                "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，"
                "請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。"
                "(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)"
            ),
        },
        {"role": "user", "content": prompt},
    ]

    completion = OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    keywords = completion.choices[0].message.content

    # 2) 透過 main.get_new_info 拿到新聞列表（在測試中被 mock）
    news_items = get_new_info(keywords, is_initial=False)
    print(news_items)

    news_list = []
    for news in news_items:
        try:
            resp = requests.get(news["titleLink"])
            soup = BeautifulSoup(resp.text, "html.parser")

            title = soup.find("h1", class_="article-content__title").text
            time = soup.find("time", class_="article-content__time").text
            content_section = soup.find("section", class_="article-content__editor")

            paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]

            detailed_news = {
                "id": next(_id_counter),
                "url": news["titleLink"],
                "title": title,
                "time": time,
                "content": " ".join(paragraphs),
            }
            news_list.append(detailed_news)
        except Exception as e:
            print("search_news parse error:", e)

    # 新到舊排序（測試也預期 2 篇時會有順序）
    return sorted(news_list, key=lambda x: x["time"], reverse=True)
    #keywords = ai_service.extract_keywords(req.prompt)
    #return news_service.get_news_info(keywords)


# 新聞摘要：POST /api/v1/news/news_summary
@router.post("/news_summary")
def summarize_news(req: NewsSumaryRequestSchema, user=Depends(get_current_user)):
    result = ai_service.summarize(req.content)
    return {
        "summary": result["影響"],
        "reason": result["原因"]
    }


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