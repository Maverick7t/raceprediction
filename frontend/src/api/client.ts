import type {
    RacePredictionsResponse,
    RaceListItem,
    StandingsResponse,
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
    getRaces: () =>
        request<RaceListItem[]>('/api/v1/races'),

    getPredictionRaces: () =>
        request<RaceListItem[]>('/api/v1/predictions/races'),

    // Predictions
    getLatestPredictions: () =>
        request<RacePredictionsResponse>('/api/v1/predictions'),

    getPredictions: (raceKey: string) =>
        request<RacePredictionsResponse>(`/api/v1/predictions/${raceKey}`),

    // Standings
    getDriverStandings: (year?: number) =>
        request<StandingsResponse>(`/api/v1/standings/drivers${year ? `?year=${year}` : ''}`),

    getConstructorStandings: (year?: number) =>
        request<StandingsResponse>(`/api/v1/standings/constructors${year ? `?year=${year}` : ''}`),

    // Health
    getHealth: () =>
        request<HealthStatus>('/api/v1/health'),
};