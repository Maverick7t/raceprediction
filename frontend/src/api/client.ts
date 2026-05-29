// src/api/client.ts
// The ONLY file in the frontend that knows the backend URL and HTTP shapes.
// Components never call fetch() directly — they use these functions.

import type {
    PredictionsResponse,
    RaceKey,
    StandingsResponse,
    DriverStanding,
    ConstructorStanding,
    HealthStatus,
} from '@/types';

// In dev: Vite proxies /api → localhost:8000 (configured in vite.config.ts)
// In prod: set VITE_API_BASE_URL to your Render backend URL
const BASE = import.meta.env.VITE_API_BASE_URL
    ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
    : '/api/v1';

// ---------------------------------------------------------------------------
// Internal fetch wrapper
// ---------------------------------------------------------------------------

async function apiFetch<T>(path: string): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        headers: { Accept: 'application/json' },
    });

    if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`API ${res.status}: ${text || res.statusText}`);
    }

    return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Predictions
// ---------------------------------------------------------------------------

/** Latest race predictions (most recent qualifying weekend) */
export function fetchLatestPredictions(): Promise<PredictionsResponse> {
    return apiFetch<PredictionsResponse>('/predictions');
}

/** Predictions for a specific race_key */
export function fetchPredictionsByRace(raceKey: string): Promise<PredictionsResponse> {
    return apiFetch<PredictionsResponse>(`/predictions/${raceKey}`);
}

/** All race keys that have stored predictions */
export function fetchPredictionRaces(): Promise<RaceKey[]> {
    return apiFetch<RaceKey[]>('/predictions/races');
}

// ---------------------------------------------------------------------------
// Standings
// ---------------------------------------------------------------------------

/** Driver championship standings for a given year */
export function fetchDriverStandings(
    year: number,
): Promise<StandingsResponse<DriverStanding>> {
    return apiFetch<StandingsResponse<DriverStanding>>(
        `/standings/drivers?year=${year}`,
    );
}

/** Constructor championship standings for a given year */
export function fetchConstructorStandings(
    year: number,
): Promise<StandingsResponse<ConstructorStanding>> {
    return apiFetch<StandingsResponse<ConstructorStanding>>(
        `/standings/constructors?year=${year}`,
    );
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export function fetchHealth(): Promise<HealthStatus> {
    return apiFetch<HealthStatus>('/health');
}

export function fetchHealthDb(): Promise<HealthStatus> {
    return apiFetch<HealthStatus>('/health/db');
}

export function fetchHealthModel(): Promise<HealthStatus> {
    return apiFetch<HealthStatus>('/health/model');
}