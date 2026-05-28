# ---------------------------------------------------------------------------
# F1 Prediction System — Production Dockerfile
#
# Single image containing:
#   - FastAPI API server (entrypoint: uvicorn main:app)
#   - ML inference code (loaded at startup by the API)
#   - Prefect worker scripts (run separately via `docker run ... python -m workers.flows.X`)
#
# Build:
#   docker build -t f1-prediction:latest .
#
# Run API locally (staging):
#   docker run --env-file .env -p 8000:8000 f1-prediction:latest
#
# Run a Prefect flow locally:
#   docker run --env-file .env f1-prediction:latest \
#     python -m workers.flows.post_race_flow 2025 5
# ---------------------------------------------------------------------------

# ---- Stage 1: dependency builder ----------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /build

# System deps for psycopg (binary) + XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirement.txt


# ---- Stage 2: runtime image ---------------------------------------------
FROM python:3.10-slim AS runtime

# Non-root user — never run as root in production
RUN groupadd --gid 1001 appgroup \
    && useradd  --uid 1001 --gid appgroup --no-create-home appuser

# Runtime system deps (libpq needed at runtime for psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup . .

# FastF1 cache dir — writable by appuser
RUN mkdir -p /tmp/fastf1_cache && chown appuser:appgroup /tmp/fastf1_cache

# Models dir — must exist; real artifacts are mounted or downloaded at startup
RUN mkdir -p /app/models && chown appuser:appgroup /app/models

USER appuser

# Render / Railway detect the PORT env var; default 8000 for local
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FASTF1_CACHE_DIR=/tmp/fastf1_cache

EXPOSE ${PORT}

# Healthcheck — Render uses this to detect a healthy deploy before routing traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Default entrypoint: run the API
# Render sets $PORT; gunicorn-style workers not needed at this scale
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]