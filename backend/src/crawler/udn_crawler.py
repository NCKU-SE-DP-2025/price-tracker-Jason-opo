from requests import Response
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import quote
import requests

from .crawler_base import NewsCrawlerBase, Headline, News
from .exceptions import DomainMismatchException


class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = "https://udn.com/api/more"
        self.timeout = timeout

    # ---------------------- Fake Headline (Unit Test Only) ---------------------- #
    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> List[Headline]:
        return [
            Headline(
                title=f"Fake UDN News about {search_term}",
                url="https://udn.com/news/fake123"
            )
        ]

    # ---------------------- Unit-Test Required Methods -------------------------- #
    def _create_search_params(self, page: int, search_term: str) -> dict:
        return {
            "page": page,
            "id": f"search:{quote(search_term)}",
            "channelId": self.CHANNEL_ID,
            "type": "searchword",
        }

    def _perform_request(self, url: str | None = None, params: dict | None = None) -> Response:
        if url is None:
            url = self.news_website_url

        # Use our BaseClass domain check!
        if not self._is_valid_url(url):
            raise DomainMismatchException(url)

        # We do not need real parsing here — mock will replace requests.get
        return requests.get(url, params=params, timeout=self.timeout)

    def _parse_headlines(self, lists: list[dict]) -> List[Headline]:
        headlines = []
        for item in lists:
            headlines.append(
                Headline(
                    title=item.get("title", ""),
                    url=item.get("titleLink", ""),
                )
            )
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> List[Headline]:
        params = self._create_search_params(page, search_term)
        response = self._perform_request(self.news_website_url, params)

        if response.status_code != 200:
            return []

        data = response.json()
        lists = data.get("lists", [])
        return self._parse_headlines(lists)

    # ---------------------- Fake Parse for Unit Test ---------------------------- #
    def parse(self, url: str) -> News:
        # Check URL domain
        if not self._is_valid_url(url):
            raise DomainMismatchException(url)

        resp = self._perform_request(url=url)
        # Mocked HTML will be parsed by BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        return self._extract_news(soup, url)

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        title = soup.find("h1", class_="article-content__title").text
        time = soup.find("time", class_="article-content__time").text
        content_section = soup.find("section", class_="article-content__editor")

        paragraphs = [
            p.get_text(strip=True)
            for p in content_section.find_all("p")
            if p.get_text(strip=True) and "▪" not in p.get_text()
        ]
        content = " ".join(paragraphs)

        return News(
            title=title,
            url=url,
            time=time,
            content=content
        )

    # ---------------------- Fake Save (Must call add & commit if DB provided) ---- #
    @staticmethod
    def save(news: News, db=None):
        if db is None:
            return True
        db.add(news)
        db.commit()
        return True