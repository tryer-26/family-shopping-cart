"""
Price Scraper Interface.

DISCLAIMER: This module is for personal/family use only.
Commercial use and high-frequency crawling are strictly prohibited.
All scraping code must include this disclaimer.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    channel_name: str
    product_url: str
    list_price: float
    final_price: float
    shipping_fee: float
    title: str = ""
    success: bool = True
    error: str = ""


class BaseScraper(ABC):
    """Abstract base class for price scrapers."""

    @abstractmethod
    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape price info from a given product URL."""
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name (e.g., 'jd', 'taobao')."""
        pass


class ScraperRegistry:
    """Registry of all available scrapers."""

    def __init__(self):
        self._scrapers: dict[str, BaseScraper] = {}

    def register(self, scraper: BaseScraper):
        self._scrapers[scraper.platform_name] = scraper
        logger.info(f"Registered scraper: {scraper.platform_name}")

    def get(self, platform: str) -> BaseScraper | None:
        return self._scrapers.get(platform)

    def get_all(self) -> list[BaseScraper]:
        return list(self._scrapers.values())

    def get_platforms(self) -> list[str]:
        return list(self._scrapers.keys())


registry = ScraperRegistry()


def detect_platform(url: str) -> str | None:
    """Detect e-commerce platform from URL."""
    url_lower = url.lower()
    if "jd.com" in url_lower:
        return "jd"
    if "taobao.com" in url_lower:
        return "taobao"
    if "tmall.com" in url_lower:
        return "tmall"
    if "pinduoduo.com" in url_lower or "yangkeduo.com" in url_lower:
        return "pdd"
    if "samscn.com" in url_lower or "samsclub" in url_lower:
        return "sams"
    if "hema" in url_lower or "freshhema" in url_lower:
        return "hema"
    return None
