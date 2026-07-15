import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.utils.logging_config import setup_logging
from app.routers import (
    auth_router, users_router, families_router, categories_router,
    products_router, prices_router, coupons_router, shopping_list_router,
    search_router, ocr_router, statistics_router, export_router, system_router,
)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped (may already exist): {e}")
    
    try:
        from app.services.meilisearch import create_index
        create_index()
    except Exception as e:
        logger.warning(f"Meilisearch initialization skipped: {e}")
    
    try:
        from app.services.scraper_example import registry
        logger.info("Example scrapers registered")
    except Exception as e:
        logger.warning(f"Scraper registration skipped: {e}")
    
    yield
    
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(families_router, prefix=settings.API_V1_PREFIX)
app.include_router(categories_router, prefix=settings.API_V1_PREFIX)
app.include_router(products_router, prefix=settings.API_V1_PREFIX)
app.include_router(prices_router, prefix=settings.API_V1_PREFIX)
app.include_router(coupons_router, prefix=settings.API_V1_PREFIX)
app.include_router(shopping_list_router, prefix=settings.API_V1_PREFIX)
app.include_router(search_router, prefix=settings.API_V1_PREFIX)
app.include_router(ocr_router, prefix=settings.API_V1_PREFIX)
app.include_router(statistics_router, prefix=settings.API_V1_PREFIX)
app.include_router(export_router, prefix=settings.API_V1_PREFIX)
app.include_router(system_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION}", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
