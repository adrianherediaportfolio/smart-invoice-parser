import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.routes import router
from src.core.config import settings
from src.core.database import init_db

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Smart Invoice Parser API ready")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Smart Invoice Parser API",
    description=(
        "REST API that extracts structured data from invoice PDFs and images "
        "using OCR (Tesseract) + AI (OpenAI). Upload any invoice and get back "
        "structured JSON with vendor info, line items, totals, and more."
    ),
    version="1.0.1",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "smart-invoice-parser", "version": "1.0.1"}
