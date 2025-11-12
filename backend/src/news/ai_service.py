import json
from openai import OpenAI
import os

class AIService:
    def __init__(self):
        self.client = OpenAI()

    def summarize(self, content: str):
        messages = [
            {"role": "system", 
             "content": (
                    "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 "
                    "(影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})"
                ),
            },
            {"role": "user", "content": content},
        ]
        result = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages
        )
        return json.loads(result.choices[0].message.content)

    def extract_keywords(self, prompt: str):
        messages = [
            {"role": "system", 
             "content": (
                    "你是一個關鍵字提取機器人，用戶將會輸入一段文字，"
                    "表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，"
                    "請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。"
                    "(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)"
                ),
            },
            {"role": "user", "content": prompt},
        ]
        result = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages
        )
        return result.choices[0].message.content.strip()
