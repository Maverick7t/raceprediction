"""
main.py — FastAPI application entrypoint.

Model loading happens at startup — the application does NOT start
in a degraded state if model files are missing. Fix the artifacts, then restart.

Rate limiting: 60 req/min per IP globally via slowapi.
CORS: allow all origins in dev, lock to Vercel domain in prod.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.router import api_router
from app.core.config import config
from app.core.logging import get_logger
from app.ml.inference.loader import get_engine

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("API startup: loading inference engine")
    try:
        engine = get_engine()
        logger.info(
            f"Inference engine ready: "
            f"model={engine.model_version} features={engine.feature_version}"
        )
    except FileNotFoundError as e:
        # Hard fail — do not start without a model
        logger.error(f"FATAL: model artifacts not found — {e}")
        raise SystemExit(1) from e

    yield
    # --- Shutdown ---
    logger.info("API shutdown")


app = FastAPI(
    title="F1 Prediction API",
    version="1.0.0",
    description="Race winner and podium predictions powered by XGBoost.",
    lifespan=lifespan,
    docs_url="/docs" if config.ENVIRONMENT == "dev" else None,
    redoc_url=None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
allowed_origins = (
    ["*"]
    if config.ENVIRONMENT == "dev"
    else [os.environ.get("FRONTEND_URL", "https://your-vercel-app.vercel.app")]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )