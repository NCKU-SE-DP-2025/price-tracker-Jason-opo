import os
from src.news.service import NewsService
from src.news.ai_service import AIService

TESTING = os.getenv("TESTING") == "1"

# 在測試模式下，不要載入 APScheduler，也不建立 scheduler
if not TESTING:
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
else:
    scheduler = None

def start_scheduler():
    if TESTING:
        print("Skipping scheduler (TESTING=1).")
        return

    from src.core.database import SessionLocal

    ai_service = AIService()
    news_service = NewsService(ai_service)

    def job():
        db = SessionLocal()
        news_service.crawl_and_save_news(db)
        db.close()

    scheduler.add_job(job, "interval", minutes=100)
    scheduler.start()

def stop_scheduler():
    if TESTING:
        return

    scheduler.shutdown()
