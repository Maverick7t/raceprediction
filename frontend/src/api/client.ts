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
    return apiFetch<any>('/predictions').then((raw) => {
        // Normalize backend field names to frontend `Prediction` shape
        return {
            ...raw,
            predictions: (raw.predictions || []).map((p: any) => ({
                driver_code: p.driver_code,
                driver_name: p.driver_name,
                team_id: p.team_id,
                race_key: p.race_key,
                qualifying_position: p.qualifying_position ?? null,
                predicted_at: p.generated_at ?? p.predicted_at,
                model_version: p.model_version,
                feature_version: p.feature_version,
                // normalized fields expected by UI
                winner_probability: p.predicted_winner_prob ?? p.winner_probability,
                podium_probability: p.predicted_podium_prob ?? p.podium_probability,
                predicted_position: p.predicted_rank ?? p.predicted_position,
            })),
        } as PredictionsResponse;
    });
}

/** Predictions for a specific race_key */
export function fetchPredictionsByRace(raceKey: string): Promise<PredictionsResponse> {
    return apiFetch<any>(`/predictions/${raceKey}`).then((raw) => {
        return {
            ...raw,
            predictions: (raw.predictions || []).map((p: any) => ({
                driver_code: p.driver_code,
                driver_name: p.driver_name,
                team_id: p.team_id,
                race_key: p.race_key,
                qualifying_position: p.qualifying_position ?? null,
                predicted_at: p.generated_at ?? p.predicted_at,
                model_version: p.model_version,
                feature_version: p.feature_version,
                winner_probability: p.predicted_winner_prob ?? p.winner_probability,
                podium_probability: p.predicted_podium_prob ?? p.podium_probability,
                predicted_position: p.predicted_rank ?? p.predicted_position,
            })),
        } as PredictionsResponse;
    });
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