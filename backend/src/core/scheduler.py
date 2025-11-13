from src.news.service import NewsService
from src.news.ai_service import AIService
import os

# pytest 模式：完全不要建立 scheduler 實例
if os.getenv("TESTING") == "1":
    scheduler = None
else:
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()

def start_scheduler():
    # pytest 模式不啟動 scheduler
    if os.getenv("TESTING") == "1":
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
    if os.getenv("TESTING") == "1":
        return

    if scheduler:
        scheduler.shutdown()
