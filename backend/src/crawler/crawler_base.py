from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, AnyHttpUrl
from tldextract import extract
from .exceptions import DomainMismatchException


class Headline(BaseModel):
    title: str
    url: str


class News(Headline):
    time: str
    content: str


class NewsCrawlerBase(ABC):
    """Base class for all news crawlers."""

    news_website_url: str = ""
    news_website_news_child_urls: list[str] = []

    @abstractmethod
    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> List[Headline]:
        pass

    @abstractmethod
    def parse(self, url: AnyHttpUrl | str) -> News:
        pass

    @staticmethod
    @abstractmethod
    def save(news: News, db=None):
        pass

    def _is_valid_url(self, url: str) -> bool:
        """Check if domain matches main site or children."""
        root_domain = extract(self.news_website_url).registered_domain
        target_domain = extract(url).registered_domain
        return target_domain == root_domain

    def validate_and_parse(self, url: str) -> News:
        if not self._is_valid_url(url):
            raise DomainMismatchException(url)
        return self.parse(url)