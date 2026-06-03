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
import PredictionGrid from '../components/PredictionGrid';
import ProbabilitySection from '../components/ProbabilitySection';
import { PodiumCard } from "../components/PodiumCard";

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

    const podium = useMemo(() => {
        return sorted
            .slice().sort((a, b) => a.predicted_rank - b.predicted_rank)
            .slice(0, 3);
    }, [sorted]);

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
            <div className="flex-1 max-w-[1700px] mx-auto w-full px-4 md:px-6 xl:px-10 py-6">


                {/* Race header */}
                {raceData && selectedRace && (
                    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-6 animate-fade-in-up">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <span
                                    className="font-f1 text-[11px] uppercase tracking-wider px-2 py-0.5 rounded-sm"
                                    style={{
                                        background: 'var(--bg-elevated)',
                                        color: 'var(--text-muted)',
                                        border: '1px solid var(--border-default)',
                                    }}
                                >
                                    Prediction
                                </span>
                                <span className="font-mono text-[11px] text-[var(--text-secondary)] tracking-wide">
                                    ROUND {selectedRace.round}
                                </span>
                            </div>
                            <h1 className="font-f1-bold text-2xl sm:text-3xl tracking-wide uppercase">
                                {selectedRace.race_name}
                            </h1>
                            <p className="font-display text-sm sm:text-base uppercase tracking-widest text-[var(--text-secondary)] mt-2">
                                {selectedRace.circuit_id}
                                <span className="mx-2 text-[var(--text-muted)]">•</span>
                                {selectedRace.race_date}
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
                                    className={`
                                    relative
                                    px-3
                                    py-2
                                    text-[10px]
                                    uppercase
                                    transition-all
                                    duration-200
                                    ${sortBy === key
                                            ? 'font-f1-bold text-white'
                                            : 'font-f1 text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                        }
    `}
                                >
                                    {label}

                                    {sortBy === key && (
                                        <span
                                            className="
                absolute
                left-0
                bottom-0
                h-[3px]
                w-full
                bg-[#e10600]
            "
                                        />
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}



                {podium.length === 3 && (
                    <div
                        className="
                        grid
                        gap-6
                        items-end
                        mb-10
                        grid-cols-1
                        xl:grid-cols-[1fr_1.35fr_1fr]
                    "
                    >

                        <PodiumCard
                            position={2}
                            firstName={podium[1].driver_name.split(" ")[0]}
                            lastName={podium[1].driver_name.split(" ").slice(1).join(" ")}
                            teamName={getTeamTheme(podium[1].team_id).name}
                            value={`${Math.round(
                                podium[1].predicted_winner_prob * 100
                            )}%`}
                            teamColor={getTeamTheme(podium[1].team_id).primary}
                            image={`/drivers/${podium[1].driver_code.toUpperCase()}.png`}
                        />

                        <PodiumCard
                            position={1}
                            firstName={podium[0].driver_name.split(" ")[0]}
                            lastName={podium[0].driver_name.split(" ").slice(1).join(" ")}
                            teamName={getTeamTheme(podium[0].team_id).name}
                            value={`${Math.round(
                                podium[0].predicted_winner_prob * 100
                            )}%`}
                            teamColor={getTeamTheme(podium[0].team_id).primary}
                            image={`/drivers/${podium[0].driver_code.toUpperCase()}.png`}
                        />

                        <PodiumCard
                            position={3}
                            firstName={podium[2].driver_name.split(" ")[0]}
                            lastName={podium[2].driver_name.split(" ").slice(1).join(" ")}
                            teamName={getTeamTheme(podium[2].team_id).name}
                            value={`${Math.round(
                                podium[2].predicted_winner_prob * 100
                            )}%`}
                            teamColor={getTeamTheme(podium[2].team_id).primary}
                            image={`/drivers/${podium[2].driver_code.toUpperCase()}.png`}
                        />

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
                        {/* <PredictionGrid predictions={sorted} /> */}

                        <ProbabilitySection predictions={sorted} />
                    </div>
                )}
            </div>
        </div>
    );
}