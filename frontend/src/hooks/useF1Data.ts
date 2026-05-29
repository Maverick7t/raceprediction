// src/hooks/useF1Data.ts
// All TanStack Query hooks. Components import from here — never from client.ts directly.
//
// Caching strategy:
//   staleTime: how long data is considered fresh (no background refetch)
//   gcTime:    how long unused data stays in cache before garbage collection
//
// Predictions are stable until the next qualifying session, so 5-minute staleTime
// avoids unnecessary refetches on tab focus while keeping data reasonably fresh.

import { useQuery } from '@tanstack/react-query';
import {
    fetchLatestPredictions,
    fetchPredictionsByRace,
    fetchPredictionRaces,
    fetchDriverStandings,
    fetchConstructorStandings,
    fetchHealthDb,
    fetchHealthModel,
} from '@/api/client';

// ---------------------------------------------------------------------------
// Predictions
// ---------------------------------------------------------------------------

export function useLatestPredictions() {
    return useQuery({
        queryKey: ['predictions', 'latest'],
        queryFn: fetchLatestPredictions,
        staleTime: 5 * 60 * 1000,   // 5 minutes
        gcTime: 30 * 60 * 1000,     // 30 minutes
        retry: 2,
    });
}

export function usePredictionsByRace(raceKey: string | null) {
    return useQuery({
        queryKey: ['predictions', raceKey],
        queryFn: () => fetchPredictionsByRace(raceKey!),
        enabled: !!raceKey,
        staleTime: 5 * 60 * 1000,
        gcTime: 30 * 60 * 1000,
        retry: 2,
    });
}

export function usePredictionRaces() {
    return useQuery({
        queryKey: ['predictions', 'races'],
        queryFn: fetchPredictionRaces,
        staleTime: 10 * 60 * 1000,  // race list changes rarely
        gcTime: 60 * 60 * 1000,
        retry: 2,
    });
}

// ---------------------------------------------------------------------------
// Standings
// ---------------------------------------------------------------------------

export function useDriverStandings(year: number) {
    return useQuery({
        queryKey: ['standings', 'drivers', year],
        queryFn: () => fetchDriverStandings(year),
        staleTime: 10 * 60 * 1000,
        gcTime: 60 * 60 * 1000,
        retry: 2,
    });
}

export function useConstructorStandings(year: number) {
    return useQuery({
        queryKey: ['standings', 'constructors', year],
        queryFn: () => fetchConstructorStandings(year),
        staleTime: 10 * 60 * 1000,
        gcTime: 60 * 60 * 1000,
        retry: 2,
    });
}

// ---------------------------------------------------------------------------
// Health (used by status banner, not the main UI)
// ---------------------------------------------------------------------------

export function useSystemHealth() {
    const db = useQuery({
        queryKey: ['health', 'db'],
        queryFn: fetchHealthDb,
        staleTime: 60 * 1000,       // re-check every minute
        gcTime: 5 * 60 * 1000,
        retry: 1,
    });

    const model = useQuery({
        queryKey: ['health', 'model'],
        queryFn: fetchHealthModel,
        staleTime: 5 * 60 * 1000,
        gcTime: 30 * 60 * 1000,
        retry: 1,
    });

    const isHealthy =
        db.data?.status === 'ok' && model.data?.status === 'ok';

    const predictionsStale = db.data?.predictions_stale === true;

    return {
        isHealthy,
        predictionsStale,
        dbStatus: db.data,
        modelStatus: model.data,
        isLoading: db.isLoading || model.isLoading,
    };
}