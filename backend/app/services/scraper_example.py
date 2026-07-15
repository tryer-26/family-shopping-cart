"""
Example scraper implementations for demonstration.

DISCLAIMER: This module is for personal/family use only.
Commercial use and high-frequency crawling are strictly prohibited.
"""

import logging
import random

from app.services.scraper import BaseScraper, ScrapeResult, registry

logger = logging.getLogger(__name__)


class ExampleJDScraper(BaseScraper):
    """Example JD.com scraper.
    
    DISCLAIMER: This is a demonstration scraper that returns mock data.
    In production, implement with Playwright browser automation.
    The actual Playwright-based implementation would navigate to the URL,
    wait for page load, extract price elements, and return real prices.
    """

    @property
    def platform_name(self) -> str:
        return "jd"

    async def scrape(self, url: str) -> ScrapeResult:
        logger.info(f"[ExampleJD] Scraping URL: {url}")
        # In production, use Playwright to:
        # 1. Launch browser (via playwright-service API)
        # 2. Navigate to product page
        # 3. Wait for price element to render
        # 4. Extract price, title, shipping info
        # 5. Return structured result
        # 
        # For now, return simulated data:
        price = round(random.uniform(10, 500), 2)
        return ScrapeResult(
            channel_name="京东",
            product_url=url,
            list_price=price,
            final_price=price,
            shipping_fee=0 if price > 49 else 6,
            title="示例商品（京东价格模拟）",
        )


class ExampleTaobaoScraper(BaseScraper):
    """Example Taobao/Tmall scraper.
    
    DISCLAIMER: Demonstration scraper with mock data.
    """

    @property
    def platform_name(self) -> str:
        return "taobao"

    async def scrape(self, url: str) -> ScrapeResult:
        logger.info(f"[ExampleTaobao] Scraping URL: {url}")
        price = round(random.uniform(8, 400), 2)
        return ScrapeResult(
            channel_name="淘宝",
            product_url=url,
            list_price=price,
            final_price=price,
            shipping_fee=0 if price > 29 else 5,
            title="示例商品（淘宝价格模拟）",
        )


# Register example scrapers
registry.register(ExampleJDScraper())
registry.register(ExampleTaobaoScraper())

logger.info("Example scrapers registered. DISCLAIMER: For personal/family use only.")
