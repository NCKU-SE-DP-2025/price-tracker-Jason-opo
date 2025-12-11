from pydantic import BaseModel

class NewsBase(BaseModel):
    url: str
    title: str
    time: str
    content: str
    summary: str
    reason: str

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int

    class Config:
        orm_mode = True
