# =============================================================================
# F1 Prediction System — Production Dockerfile
# Two-stage build: builder installs deps, runtime is lean.
# Non-root user. HEALTHCHECK wired to /api/v1/health.
# =============================================================================

# --------------------------------------------------------------------------- #
# Stage 1 — Builder                                                           #
# --------------------------------------------------------------------------- #
FROM python:3.10-slim AS builder

WORKDIR /build

# Build tools needed only for C extensions (psycopg3, XGBoost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --------------------------------------------------------------------------- #
# Stage 2 — Runtime                                                           #
# --------------------------------------------------------------------------- #
FROM python:3.10-slim AS runtime

# Runtime dependencies only (libpq for psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Non-root user — principle of least privilege
RUN useradd --no-create-home --shell /bin/bash appuser

WORKDIR /app

# Copy application code
COPY . .

# Create directories the app needs at runtime
# models/ is gitignored — will be populated from Supabase Storage on startup
RUN mkdir -p models mlruns /tmp/fastf1_cache \
    && chown -R appuser:appuser /app /tmp/fastf1_cache

USER appuser

# Render sets PORT dynamically; default to 8000 for local Docker runs
ENV PORT=8000

EXPOSE ${PORT}

# Health check — Render uses this before routing traffic to the new container.
# Checks every 30s; 3 failures = unhealthy → Render keeps old container running.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# uvicorn workers: 1 on free tier (512MB RAM).
# Bump to 2-4 workers when upgrading to the $7/month paid plan.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level info"]