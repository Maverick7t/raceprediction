export interface RaceListItem {
    race_key: string;
    year: number;
    round: number;
    race_name: string;
    circuit_id: string;
    has_predictions?: boolean;
}

export interface RacesResponse {
    count: number;
    races: RaceListItem[];
}

export interface PredictionRaceKeysResponse {
    races: string[];
}

export interface RacePrediction {
    race_key: string;
    driver_code: string;
    driver_name: string;
    team_id: string;
    qualifying_position: number | null;
    predicted_winner_prob: number;
    predicted_podium_prob: number;
    predicted_rank: number;
    model_version: string;
    feature_version: string;
    generated_at: string;
}

export interface RacePredictionsResponse {
    race_key: string;
    generated_at: string;
    model_version: string;
    feature_version: string;
    predictions: RacePrediction[];
}

export interface DriverStanding {
    position: number;
    driver_code: string;
    driver_name: string;
    team: string;
    points: number;
    wins: number;
    round: number;
}

export interface ConstructorStanding {
    position: number;
    team_id: string;
    team: string;
    points: number;
    wins: number;
    round: number;
}

export interface DriverStandingsResponse {
    year: number;
    standings: DriverStanding[];
}

export interface ConstructorStandingsResponse {
    year: number;
    standings: ConstructorStanding[];
}

export interface HealthStatus {
    status: 'ok' | 'degraded' | 'error';
    timestamp: string;
}

export interface HealthDbStatus {
    status: 'ok' | 'degraded';
    db_connected: boolean;
    predictions_stale: boolean | null;
    predictions_age_days: number | null;
    last_prediction_at?: string;
    detail?: string;
    staleness_check_error?: string;
}

export interface HealthModelStatus {
    status: 'ok' | 'not_loaded' | 'error';
    detail?: string;
    model_version?: string;
    feature_version?: string;
    feature_columns?: number;
}