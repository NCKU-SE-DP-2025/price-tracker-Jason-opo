from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import user_news_association_table  # 注意防循環匯入問題

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    time = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)

    # 關聯 - 哪些使用者按讚這篇新聞
    upvoted_by_users = relationship(
        "User",
        secondary=user_news_association_table,
        back_populates="upvoted_news"
    )
