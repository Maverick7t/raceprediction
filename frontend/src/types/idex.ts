// src/types/index.ts
// Matches the FastAPI response shapes from /api/v1/ routes exactly.
// Update these whenever the backend schema changes.

// ---------------------------------------------------------------------------
// Predictions
// ---------------------------------------------------------------------------

export interface Prediction {
    driver_code: string;
    driver_name: string;
    team_id: string;
    race_key: string;
    predicted_position: number;
    winner_probability: number;
    podium_probability: number;
    qualifying_position: number | null;
    predicted_at: string; // ISO timestamp
}

export interface PredictionsResponse {
    race_key: string;
    race_name: string | null;
    predictions: Prediction[];
    generated_at: string;
}

export interface RaceKey {
    race_key: string;
}

// ---------------------------------------------------------------------------
// Standings
// ---------------------------------------------------------------------------

export interface DriverStanding {
    driver_code: string;
    driver_name: string;
    team: string;
    team_id: string;
    position: number;
    points: number;
    wins: number;
    year: number;
}

export interface ConstructorStanding {
    team_id: string;
    team: string;
    position: number;
    points: number;
    wins: number;
    year: number;
}

export interface StandingsResponse<T> {
    year: number;
    standings: T[];
    updated_at: string | null;
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export interface HealthStatus {
    status: 'ok' | 'error';
    db_connected?: boolean;
    predictions_stale?: boolean;
    model_version?: string;
    feature_columns?: number;
    message?: string;
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------

/** Team ID → hex color for the car livery accent */
export const TEAM_COLORS: Record<string, string> = {
    red_bull: '#3671C6',
    ferrari: '#E8002D',
    mercedes: '#27F4D2',
    mclaren: '#FF8000',
    aston_martin: '#229971',
    alpine: '#FF87BC',
    williams: '#64C4FF',
    rb: '#6692FF',
    haas: '#B6BABD',
    kick_sauber: '#52E252',
    sauber: '#52E252',
};

export function getTeamColor(teamId: string): string {
    return TEAM_COLORS[teamId.toLowerCase()] ?? '#666688';
}

/** Format race_key → human readable: "bahrain_grand_prix_2024" → "Bahrain Grand Prix 2024" */
export function formatRaceKey(raceKey: string): string {
    return raceKey
        .replace(/_(\d{4})$/, ' $1')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

/** Format a probability to a percentage string: 0.9137 → "91.4%" */
export function formatPct(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
}

/** Podium finish position → medal color */
export function podiumColor(position: number): string {
    if (position === 1) return '#FFD700';
    if (position === 2) return '#C0C0C0';
    if (position === 3) return '#CD7F32';
    return 'transparent';
}