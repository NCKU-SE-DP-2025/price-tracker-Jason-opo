from pydantic import BaseModel

class UserNewsUpvote(BaseModel):
    user_id: int
    news_id: int