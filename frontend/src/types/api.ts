// All types mirror FastAPI response shapes.
// If field names differ in your schema, update here only — no other files need to change.

export interface RacePrediction {
    driver_code: string;
    driver_name?: string;
    team_id: string;
    qualifying_position: number;
    win_probability: number;
    podium_probability: number;
    predicted_finish: number;
    actual_finish?: number | null;
}

export interface RacePredictionsResponse {
    race_key: string;
    race_name: string;
    circuit_id: string;
    round: number;
    season: number;
    race_date: string;
    generated_at: string;
    model_version?: string;
    predictions: RacePrediction[];
}

export interface RaceListItem {
    race_key: string;
    race_name: string;
    circuit_id: string;
    round: number;
    season: number;
    race_date: string;
    country?: string;
    has_predictions: boolean;
    is_completed: boolean;
}

export interface DriverStanding {
    position: number;
    driver_code: string;
    driver_name: string;
    team_id: string;
    nationality?: string;
    points: number;
    wins: number;
    podiums?: number;
}

export interface ConstructorStanding {
    position: number;
    constructor_id: string;
    constructor_name: string;
    nationality?: string;
    points: number;
    wins: number;
}

export interface StandingsResponse {
    season: number;
    last_updated: string;
    drivers?: DriverStanding[];
    constructors?: ConstructorStanding[];
}

export interface HealthStatus {
    status: 'ok' | 'degraded' | 'error';
    version?: string;
    model_loaded?: boolean;
    db_connected?: boolean;
}