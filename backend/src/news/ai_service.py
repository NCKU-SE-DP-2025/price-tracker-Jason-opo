import os
import json

class AIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def _get_client(self):
        """
        在執行 summarize / extract_keywords 時才 import main.OpenAI
        這樣 pytest 的 patch("main.OpenAI") 一定已經生效
        """
        from main import OpenAI

        # pytest 模式（沒有 API key）→ 用 mock OpenAI() 就好
        if self.api_key:
            return OpenAI(api_key=self.api_key)
        else:
            # 沒 API key（pytest 模式）→ 使用 mock 的 OpenAI
            return OpenAI()
        
    def summarize(self, content: str):
        client = self._get_client()

        messages = [
            {"role": "system", 
             "content": (
                    "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 "
                    "(影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})"
                ),
            },
            {"role": "user", "content": content},
        ]

        result = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = messages
        )

        return json.loads(result.choices[0].message.content)

    def extract_keywords(self, prompt: str):
        client = self._get_client()

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

        result = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = messages
        )
        return result.choices[0].message.content.strip()
