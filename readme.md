# F1 Prediction System

A production grade Formula 1 race prediction engine that ingests qualifying and telemetry data from multiple APIs, engineers rolling features, trains XGBoost classifiers, and serves winner/podium probabilities through a versioned REST API fully automated across an entire race season with no manual intervention.

---

## What Is This

An end-to-end ML system built around the F1 race calendar. After each qualifying session it automatically:

1. Fetches qualifying results and lap times from three external APIs
2. Validates every row against typed schemas, logging failures to an audit table
3. Computes 14 rolling driver, team, circuit, and session features per driver
4. Runs inference with a trained XGBoost model and writes ranked predictions to the database
5. Exposes those predictions through a FastAPI read layer within minutes of qualifying ending

Training runs automatically when enough new race results have accumulated. A promotion gate prevents any model that doesn't improve on at least 2 of 3 key metrics from reaching production.

---



## System Architecture


The platform follows a modular monolith architecture with automated race weekend data pipelines, offline machine learning inference, and a read optimized API layer.

---

### 1. System Context

This diagram shows the system from a stakeholder perspective.

```mermaid
flowchart LR

    User["F1 Fans & Analysts"]

    Frontend["React Frontend<br/>Vercel"]

    API["FastAPI Prediction API"]

    Sources["FastF1<br/>Jolpica / Ergast<br/>OpenF1"]

    User --> Frontend
    Frontend --> API
    Sources --> API
```

---

### 2. Platform Architecture

This diagram shows the major containers and how data moves through the platform.

```mermaid
flowchart LR

    Sources["External APIs<br/>FastF1 · Ergast · OpenF1"]

    Workers["Data Pipelines<br/>Prefect Flows"]

    Database["Supabase PostgreSQL"]

    ML["ML Platform<br/>Training + Inference"]

    API["FastAPI Backend"]

    Frontend["React Frontend"]

    Users["Users"]

    Sources --> Workers
    Workers --> Database

    Database --> ML
    ML --> Database

    Database --> API

    API --> Frontend
    Frontend --> Users
```

---

### 3. End-to-End Prediction Pipeline

This diagram shows how predictions are produced after qualifying sessions.

```mermaid
flowchart LR

    APIs["FastF1 / Ergast / OpenF1"]

    Ingestion["Ingestion Flow"]

    Validation["Pandera Validation"]

    Raw["Raw Tables"]

    Features["Feature Engineering"]

    Training["XGBoost Training"]

    Registry["MLflow"]

    Artifacts["Model Artifacts"]

    Inference["Offline Inference"]

    Predictions["Predictions Table"]

    API["FastAPI"]

    Frontend["React"]

    APIs --> Ingestion
    Ingestion --> Validation
    Validation --> Raw

    Raw --> Features

    Features --> Training
    Training --> Registry
    Registry --> Artifacts

    Features --> Inference
    Artifacts --> Inference

    Inference --> Predictions

    Predictions --> API
    API --> Frontend
```

---

### 4. Backend Architecture

The backend follows a layered architecture. HTTP routes remain thin while business logic and persistence concerns are separated.

```mermaid
flowchart LR

    Routes["API Routes"]

    Services["Service Layer"]

    Repositories["Repository Layer"]

    Database["Supabase PostgreSQL"]

    Inference["Inference Engine"]

    Artifacts["Model Artifacts"]

    Routes --> Services

    Services --> Repositories
    Repositories --> Database

    Services --> Inference
    Inference --> Artifacts
```

---

### 5. Infrastructure & Operations

Production deployment, monitoring, and CI/CD.

```mermaid
flowchart LR

    GitHub["GitHub Actions"]

    Render["Render"]

    Vercel["Vercel"]

    Supabase["Supabase"]

    Sentry["Sentry"]

    BetterStack["Better Stack"]

    GitHub --> Render
    GitHub --> Vercel

    Render --> Supabase

    Render -. Logs .-> Sentry
    Render -. Metrics .-> BetterStack
```

---

### Key Architectural Decisions

#### Offline Inference

Predictions are generated immediately after qualifying and stored in the database.

**Benefits**

* Low API latency
* Predictable infrastructure cost
* No model execution during requests

**Trade-offs**

* Predictions update only when the pipeline runs

---

#### Feature Versioning

Every feature row contains a `feature_version`.

**Benefits**

* Reproducible training runs
* Safe feature evolution
* Historical model compatibility

**Trade-offs**

* Additional storage overhead

---

#### Modular Monolith

API, ML, workers, repositories, and services are deployed as a single application.

**Benefits**

* Simpler deployment model
* Lower operational complexity
* Faster development velocity

**Trade offs**

* Independent component scaling is limited

---

#### Read-Optimized API

The API serves precomputed predictions rather than generating predictions at request time.

**Benefits**

* Consistent response times
* Reduced infrastructure requirements
* Better fault isolation

**Trade offs**

* Predictions are not real-time

---
## How It Works

```
External APIs (FastF1 · Ergast/Jolpica · OpenF1)
        │
        ▼

  Prefect Flows  ──── GitHub Actions (schedule / trigger)
        │
        ▼

  Pandera Validation  →  validation_failures audit table
        │
        ▼

  qualifying_raw · results_raw · telemetry_raw   (Supabase / Postgres)
        │
        ▼

  Feature Engineering  →  features_by_race  (versioned, v1/v2/...)
        │
        ▼

  XGBoost Training  →  MLflow experiment registry
        │  (time-based split, auto-promotion gate)
        ▼

  models/ (xgb_winner.json · xgb_podium.json · metadata.json)
        │  (persisted to Supabase Storage, survives Render redeploys)
        ▼

  FastAPI  ─── /api/v1/predictions · /standings · /races · /health
        │
        ▼

  React / Vite Frontend  (Vercel)
```

**Pipeline triggers** are handled by GitHub Actions workflows on known race weekend dates (post qualifying Saturday, post race Sunday). Flows are Prefect decorated Python scripts run directly via `python -m workers.flows.<flow>`, so there is no dependency on Prefect Cloud.

**Feature versioning** — every row in `features_by_race` carries a `feature_version` column (`v1`, `v2`, …). Training and inference always read the same version. Adding or renaming a feature bumps the version; old rows remain queryable.

**Graceful degradation** — FastF1 and OpenF1 failures are non-fatal. If telemetry is unavailable, the pipeline continues with Ergast data only. If the model is missing at startup, the API refuses to start rather than serving stale or empty responses. The `/health/db` endpoint flags prediction staleness if the last stored prediction is older than 10 days during race season.

---

## Model Performance

Validated on the 2025 season (24 races), trained on 2018–2024 (2 976 rows):

| Metric | Value |
|---|---|
| Winner exact accuracy | **66.7 %** |
| Actual winner in top-3 predictions | **100 %** |
| Podium binary accuracy | **89.5 %** |

Feature importance leaders: `qualifying_position`, `podium_rate`, `avg_quali_last_5`, `constructor_form`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI · Uvicorn · slowapi (rate limiting) |
| ML | XGBoost · scikit-learn · MLflow · Pandas · Pandera |
| Data sources | FastF1 · Ergast/Jolpica · OpenF1 |
| Database | Supabase (Postgres) · SQLAlchemy · Alembic |
| Orchestration | Prefect (decorated flows) · GitHub Actions |
| Observability | Sentry · Better Stack · structured JSON logging |
| Deployment | Render (Docker, 2-stage build) · Vercel (frontend) |
| Frontend | React 19 · Vite · TanStack Query · Tailwind CSS |
| Testing | pytest · Pandera schema tests · FastAPI TestClient |

---



## Running It Yourself

### Prerequisites

- Python 3.10+, Conda (env name `f1env`)
- Supabase project (Postgres + Storage bucket named `models`)
- `.env` file — copy `.env.example` and fill in values

```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://[ref].supabase.co
SUPABASE_SERVICE_KEY=...
API_SECRET_KEY=...
SENTRY_DSN=          # optional
BETTERSTACK_TOKEN=   # optional
```

### Local run

```bash

#front end
npm run dev

# Start API
uvicorn main:app --reload --port 8000
```

### Docker

```bash
docker build -f backend/Dockerfile -t f1-api ./backend
docker run -p 8000:8000 --env-file .env f1-api
```

## API Endpoints

```
GET /api/v1/predictions                    → latest race predictions (ranked)
GET /api/v1/predictions/{race_key}         → predictions for a specific race
GET /api/v1/predictions/races              → all race keys with stored predictions
GET /api/v1/standings/drivers?year=        → driver championship standings
GET /api/v1/standings/constructors?year=
GET /api/v1/races                          → all qualifying sessions in the database
GET /api/v1/health                         → process alive
GET /api/v1/health/db                      → DB reachable + prediction staleness check
GET /api/v1/health/model                   → model loaded, version, feature count
```

All responses are JSON. Routes are read-only and public. Writes (retrain trigger, winner update) require a bearer token.

---

## CI/CD

GitHub Actions runs on every push to `main`:

```
lint → unit tests → integration tests → Docker build → Render deploy
```

Race-weekend triggers fire on known dates (post-qualifying Saturday, post-race Sunday). A weekly cron syncs standings every Monday 06:00 UTC. All jobs are idempotent — re-running never creates duplicates.

---

## Key Design Decisions

- **No inference at request time.** Predictions are computed offline and stored. The API is a database read bounded by Supabase query latency.
- **Feature versioning.** `feature_version` on every row. Mixing versions in one training run is a hard error.
- **Time-based train/val split only.** Random splits leak future race data into training.
- **Promotion gate.** A new model must beat production on ≥ 2 of 3 metrics by a minimum margin. Logging to MLflow regardless.
- **Idempotent writes everywhere.** All upserts use `ON CONFLICT DO UPDATE`. Re-running any flow is always safe.
- **Model artifacts in Supabase Storage.** Render free tier has no persistent disk. Artifacts survive redeploys via download-on-startup in the loader.
- ** best to upgrade to paid sources