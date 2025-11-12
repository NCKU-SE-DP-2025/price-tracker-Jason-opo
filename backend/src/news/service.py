import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete
from src.news.models import NewsArticle
from src.auth.models import user_news_association_table

# 共用的 HTTP 標頭（很重要，避免 403 / 空資料）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://udn.com/",
    "Connection": "keep-alive",
}

def toggle_upvote(article_id: int, user_id: int, db: Session):
    existing_upvote = db.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == article_id,
            user_news_association_table.c.user_id == user_id
        )
    ).scalar()

    if existing_upvote:
        db.execute(
            delete(user_news_association_table).where(
                user_news_association_table.c.news_articles_id == article_id,
                user_news_association_table.c.user_id == user_id
            )
        )
        db.commit()
        return "Upvote removed"
    else:
        db.execute(
            insert(user_news_association_table).values(
                news_articles_id=article_id, user_id=user_id
            )
        )
        db.commit()
        return "Article upvoted"


class NewsService:
    def __init__(self, ai_service):
        self.ai = ai_service

    def get_news_info(self, keyword: str, is_initial: bool = False):
        """
        呼叫 UDN 搜尋 API 取得新聞列表。
        重要：一定要帶 headers；若回傳格式怪或錯誤，穩定回傳 []。
        """
        url = "https://udn.com/api/more"
        pages = range(1, 10) if is_initial else [1]
        results = []
        for i in pages:
            params = {
                "page": i,
                "id": f"search:{quote(keyword)}",
                "channelId": 2,
                "type": "searchword",
            }
            try:
                resp = requests.get(url, params=params, headers=HEADERS, timeout=8)
                if resp.status_code != 200:
                    # 被擋或臨時錯誤時，略過這一頁
                    continue
                data = resp.json()
                lists = data.get("lists", [])
                if isinstance(lists, list):
                    results.extend(lists)
            except Exception:
                # 網路 / 解析錯誤都略過，維持穩定
                continue

        return results

    def crawl_and_save_news(self, db: Session):
        """
        以固定關鍵字「價格」抓新聞、進入文章頁抓全文，丟給 AI 產摘要後寫入 DB。
        - 帶 headers
        - 避免重複 URL
        - content 僅存內文，不要塞 AI 提示字串
        """
        keyword = "價格"
        for news in self.get_news_info(keyword):
            try:
                article_url = news.get("titleLink")
                if not article_url:
                    continue

                # 先檢查是否已存在，避免 UNIQUE 衝突
                exists = db.query(NewsArticle).filter(NewsArticle.url == article_url).first()
                if exists:
                    continue

                # 抓取文章頁
                resp = requests.get(article_url, headers=HEADERS, timeout=10)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                title_el = soup.find("h1", class_="article-content__title")
                time_el = soup.find("time", class_="article-content__time")
                content_section = soup.find("section", class_="article-content__editor")

                if not title_el or not time_el or not content_section:
                    continue

                title = title_el.get_text(strip=True)
                time_text = time_el.get_text(strip=True)

                paragraphs = [
                    p.get_text(strip=True)
                    for p in content_section.find_all("p")
                    if p.get_text(strip=True)
                    and "▪" not in p.get_text()  # 你的原始排除規則保留
                ]
                if not paragraphs:
                    continue

                full_text = " ".join(paragraphs)

                # AI 摘要（注意：需要正確的 OPENAI_API_KEY 才會通）
                result = self.ai.summarize(full_text)
                summary = result.get("影響", "")
                reason = result.get("原因", "")

                article = NewsArticle(
                    url=article_url,
                    title=title,
                    time=time_text,
                    content=full_text,        # ✅ 不再塞 AI 提示字串
                    summary=summary,
                    reason=reason,
                )
                db.add(article)
                db.commit()

            except Exception as e:
                # 不中斷整體流程，單篇失敗就跳過
                print("Error parsing:", e)


def get_article_upvote_details(article_id: int, user_id: int, db: Session):
    """
    回傳 (upvotes, is_upvoted)
    """
    upvotes = (
        db.query(user_news_association_table)
        .filter(user_news_association_table.c.news_articles_id == article_id)
        .count()
    )

    is_upvoted = False
    if user_id:
        vote = (
            db.query(user_news_association_table)
            .filter(
                user_news_association_table.c.news_articles_id == article_id,
                user_news_association_table.c.user_id == user_id,
            )
            .first()
        )
        is_upvoted = vote is not None

    return upvotes, is_upvoted