import requests

class PricesService:
    BASE_URL = "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice"

    def get_prices(self, category=None, commodity=None):
        try:
            response = requests.get(
                self.BASE_URL,
                params={"CategoryName": category, "Name": commodity},
                timeout=10
            )

            if response.status_code != 200:
                print(f"⚠️ API 錯誤狀態碼: {response.status_code}")
                return {"error": f"API returned status {response.status_code}"}

            try:
                return response.json()
            except ValueError:
                print("無法解析 JSON，伺服器回傳內容:")
                print(response.text[:200])
                return {"error": "Response is not JSON", "raw": response.text[:200]}

        except requests.RequestException as e:
            print("Requests 連線錯誤:", e)
            return {"error": "Connection failed"}