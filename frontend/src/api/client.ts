import type {
    ConstructorStandingsResponse,
    DriverStandingsResponse,
    HealthDbStatus,
    HealthModelStatus,
    RacePredictionsResponse,
    RaceListItem,
    RacesResponse,
    PredictionRaceKeysResponse,
    HealthStatus,
} from '../types/api';

const BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json', ...opts?.headers },
        ...opts,
    });
    if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(`${res.status} ${res.statusText}${body ? ': ' + body : ''}`);
    }
    return res.json() as Promise<T>;
}

export const api = {
    // Races
    getRaces: async () => {
        const [racesResponse, predictionKeysResponse] = await Promise.all([
            request<RacesResponse>('/api/v1/races'),
            request<PredictionRaceKeysResponse>('/api/v1/predictions/races'),
        ]);

        const predictionKeys = new Set(predictionKeysResponse.races);
        return racesResponse.races
            .map((race) => ({
                ...race,
                has_predictions: predictionKeys.has(race.race_key),
            }))
            .sort((a, b) => b.year - a.year || b.round - a.round);
    },

    getPredictionRaces: async () => {
        const races = await api.getRaces();
        return races.filter((race) => race.has_predictions);
    },

    // Predictions
    getLatestPredictions: () =>
        request<RacePredictionsResponse>('/api/v1/predictions'),

    getPredictions: (raceKey: string) =>
        request<RacePredictionsResponse>(`/api/v1/predictions/${raceKey}`),

    // Standings
    getDriverStandings: (year?: number) =>
        request<DriverStandingsResponse>(`/api/v1/standings/drivers${year ? `?year=${year}` : ''}`),

    getConstructorStandings: (year?: number) =>
        request<ConstructorStandingsResponse>(`/api/v1/standings/constructors${year ? `?year=${year}` : ''}`),

    // Health
    getHealth: () =>
        request<HealthStatus>('/api/v1/health'),

    getHealthDb: () =>
        request<HealthDbStatus>('/api/v1/health/db'),

    getHealthModel: () =>
        request<HealthModelStatus>('/api/v1/health/model'),
};