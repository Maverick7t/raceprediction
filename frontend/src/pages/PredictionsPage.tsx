import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { RacePrediction, RaceListItem } from '../types/api';
import { RaceSelector } from '../components/RaceSelector';
import { ProbabilityBar } from '../components/ProbabilityBar';
import { TeamBadge, TeamAccent } from '../components/TeamBadge';
import { LoadingState, ErrorState, EmptyState } from '../components/LoadingError';
import { getTeamTheme } from '../utils/teamColors';
import { ordinal } from '../utils/format';
import HeroRaceCard from '../components/HeroRaceCard';
import PredictionGrid from '../components/PredictionGrid';
import ProbabilitySection from '../components/ProbabilitySection';

// Medal color for top 3 finishers
function positionColor(pos: number) {
    if (pos === 1) return 'var(--accent-gold)';
    if (pos === 2) return 'var(--accent-silver)';
    if (pos === 3) return 'var(--accent-bronze)';
    return 'var(--text-muted)';
}

type SortKey = 'predicted_rank' | 'predicted_winner_prob' | 'predicted_podium_prob' | 'qualifying_position';

export function PredictionsPage() {
    const [selectedKey, setSelectedKey] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState<SortKey>('predicted_rank');

    // Race list
    const { data: races, isLoading: racesLoading, error: racesError } = useQuery({
        queryKey: ['prediction-races'],
        queryFn: api.getPredictionRaces,
        staleTime: 5 * 60_000,
    } as any);

    useEffect(() => {
        if (!selectedKey && races && races.length > 0) {
            setSelectedKey(races[0].race_key);
        }
    }, [races, selectedKey]);

    const selectedRace = useMemo<RaceListItem | null>(
        () => races?.find((race) => race.race_key === selectedKey) ?? null,
        [races, selectedKey],
    );

    // Predictions for selected race
    const { data: raceData, isLoading: predLoading, error: predError } = useQuery({
        queryKey: ['predictions', selectedKey],
        queryFn: () => api.getPredictions(selectedKey!),
        enabled: !!selectedKey,
        staleTime: 5 * 60_000,
    });

    // Sort predictions
    const sorted = useMemo<RacePrediction[]>(() => {
        if (!raceData?.predictions) return [];
        const list = [...raceData.predictions];
        list.sort((a, b) => {
            if (sortBy === 'predicted_rank') return a.predicted_rank - b.predicted_rank;
            if (sortBy === 'qualifying_position') return (a.qualifying_position ?? 99) - (b.qualifying_position ?? 99);
            return (b[sortBy] as number) - (a[sortBy] as number);
        });
        return list;
    }, [raceData, sortBy]);

    // ── Render ─────────────────────────────────────
    return (
        <div className="flex flex-col h-full">

            {/* Race selector strip */}
            <div style={{ borderBottom: '1px solid var(--border-default)', background: 'var(--bg-surface)' }}>
                {racesLoading ? (
                    <div className="px-4 py-3 font-mono text-xs text-[var(--text-muted)]">Loading races…</div>
                ) : racesError ? (
                    <div className="px-4 py-3 font-mono text-xs text-[var(--accent-red)]">Failed to load races</div>
                ) : (
                    <RaceSelector
                        races={races ?? []}
                        selectedKey={selectedKey}
                        onSelect={setSelectedKey}
                    />
                )}
            </div>

            {/* ── Main content ─────────────────────────── */}
            <div className="flex-1 max-w-5xl mx-auto w-full px-4 py-6">

                {/* Hero Race Card */}
                {raceData && selectedRace && raceData.predictions && raceData.predictions.length > 0 && (
                    <div className="mb-12 animate-fade-in-up">
                        {(() => {
                            const topPrediction = raceData.predictions[0];
                            const teamTheme = getTeamTheme(topPrediction.team_id || '');

                            return (
                                <HeroRaceCard
                                    raceName={selectedRace.race_name}
                                    round={selectedRace.round}
                                    raceDate={raceData.generated_at}
                                    winner={topPrediction.driver_name || topPrediction.driver_code}
                                    team={teamTheme.name}
                                    probability={Math.round((topPrediction.predicted_winner_prob || 0) * 100)}
                                />
                            );
                        })()}
                    </div>
                )}

                {/* Race header */}
                {raceData && selectedRace && (
                    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-6 animate-fade-in-up">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span
                                    className="font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm"
                                    style={{
                                        background: 'var(--bg-elevated)',
                                        color: 'var(--text-muted)',
                                        border: '1px solid var(--border-default)',
                                    }}
                                >
                                    Prediction snapshot
                                </span>
                                <span className="font-mono text-[10px] text-[var(--text-muted)]">
                                    {selectedRace.year} · Round {selectedRace.round}
                                </span>
                            </div>
                            <h1 className="font-display font-bold text-2xl sm:text-3xl text-[var(--text-primary)] tracking-wide">
                                {selectedRace.race_name}
                            </h1>
                            <p className="font-mono text-xs text-[var(--text-muted)] mt-0.5">
                                {selectedRace.circuit_id} · Generated {raceData.generated_at}
                            </p>
                        </div>

                        {/* Sort selector */}
                        <div className="flex items-center gap-1">
                            {(
                                [
                                    { key: 'predicted_winner_prob', label: 'Winner %' },
                                    { key: 'predicted_podium_prob', label: 'Podium %' },
                                    { key: 'predicted_rank', label: 'Rank' },
                                    { key: 'qualifying_position', label: 'Grid' },
                                ] as { key: SortKey; label: string }[]
                            ).map(({ key, label }) => (
                                <button
                                    key={key}
                                    onClick={() => setSortBy(key)}
                                    className={`px-2.5 py-1 text-[10px] font-mono uppercase tracking-widest rounded-sm border transition-colors ${sortBy === key
                                        ? 'border-[var(--accent-red)] text-[var(--accent-red)] bg-[var(--accent-red)]/10'
                                        : 'border-[var(--border-default)] text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Prediction Grid */}
                {predLoading ? (
                    <LoadingState label="Fetching predictions…" />
                ) : predError ? (
                    <ErrorState error={predError as Error} />
                ) : sorted.length === 0 ? (
                    <EmptyState label="No predictions for this race" />
                ) : (
                    <div className="space-y-12">
                        <PredictionGrid predictions={sorted} />

                        <ProbabilitySection predictions={sorted} />
                    </div>
                )}
            </div>
        </div>
    );
}