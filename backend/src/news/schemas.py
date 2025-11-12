from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class NewsSummaryRequest(BaseModel):
    content: str
 