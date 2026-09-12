import os
import sys
import types
import logging
import warnings
import sklearn._loss
import sklearn.ensemble

# Handle sklearn GradientBoosting _loss module & CyHalfBinomialLoss compatibility across versions
loss_mod = types.ModuleType('_loss')
for k, v in sklearn._loss.__dict__.items():
    setattr(loss_mod, k, v)
for k, v in sklearn.ensemble.__dict__.items():
    if not hasattr(loss_mod, k):
        setattr(loss_mod, k, v)
if hasattr(sklearn._loss, 'HalfBinomialLoss'):
    setattr(loss_mod, 'CyHalfBinomialLoss', sklearn._loss.HalfBinomialLoss)
sys.modules['_loss'] = loss_mod

# Suppress sklearn unpickling warnings and font warnings
warnings.filterwarnings("ignore")
logging.getLogger("matplotlib").setLevel(logging.ERROR)
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

import matplotlib
matplotlib.use("Agg")
try:
    import matplotlib.font_manager
    _ = matplotlib.font_manager.fontManager
except Exception:
    pass

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from database.connection import engine, Base
from backend.router import router

# Set up logging configuration
logging.basicConfig(
    level=logging.getLevelName(settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Explainable AI Loan Approval Prediction and Fairness Support API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set CORS middleware (supports cross-origin calls from frontend dashboards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Initialize Database Tables
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    try:
        # Create all tables if they don't already exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database tables: {str(e)}", exc_info=True)
        raise e
    logger.info("================================================================")
    logger.info(f"🚀 {settings.APP_NAME} active at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📖 OpenAPI Swagger Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"💚 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    logger.info("================================================================")

# Register endpoint router
app.include_router(router, prefix="")

@app.get("/")
def read_root():
    return FileResponse("dashboard/index.html")

# Mount static files from dashboard/ directory to serve the frontend SPA
# Placed after API routes so it doesn't override them
app.mount("/", StaticFiles(directory="dashboard"), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    reload_flag = settings.RELOAD and settings.ENVIRONMENT == "development"
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=reload_flag,
        reload_dirs=["backend", "config"] if reload_flag else None,
        reload_excludes=["artifacts/*", "logs/*", "*.db", "*.csv", "models_saved/*", "catboost_info/*", ".git/*"] if reload_flag else None
    )
