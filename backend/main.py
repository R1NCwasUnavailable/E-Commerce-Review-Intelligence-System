import logging
from fastapi import FastAPI, Request
import time
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sentiment
from app.services.sentiment_service import init_models, models

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing ML models...")
    init_models()
    yield
    # Shutdown logic
    logger.info("Shutting down and cleaning up models...")
    models.clear()

app = FastAPI(title="Review Intelligence API", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-Powered E-commerce Review Intelligence System API"}
