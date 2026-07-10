from app.tasks.price_scraper import scrape_product_price, batch_scrape_prices
from app.tasks.ocr_tasks import process_ocr_recognition
from app.tasks.scheduled import check_low_stock, check_expiring_coupons, scheduled_price_scrape
