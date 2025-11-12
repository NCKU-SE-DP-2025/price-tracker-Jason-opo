from apscheduler.schedulers.background import BackgroundScheduler
from src.news.service import NewsService
from src.news.ai_service import AIService
from src.core.database import SessionLocal

scheduler = BackgroundScheduler()

def start_scheduler():
    ai_service = AIService()
    news_service = NewsService(ai_service)

    def job():
        db = SessionLocal()
        news_service.crawl_and_save_news(db)
        db.close()

    scheduler.add_job(job, "interval", minutes=100)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
