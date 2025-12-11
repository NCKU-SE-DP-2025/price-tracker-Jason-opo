from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# 關聯表（多對多）
user_news_association_table = Table(
    "user_news_upvotes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("news_id", Integer, ForeignKey("news.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)

    # 關聯 - 使用者按讚過哪些新聞
    upvoted_news = relationship(
        "News",
        secondary=user_news_association_table,
        back_populates="upvoted_by_users"
    )
