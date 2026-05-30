import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { RacePrediction } from '../types/api';
import { RaceSelector } from '../components/RaceSelector';
import { ProbabilityBar } from '../components/ProbabilityBar';
import { TeamBadge, TeamAccent } from '../components/TeamBadge';
import { LoadingState, ErrorState, EmptyState } from '../components/LoadingError';
import { getTeamTheme } from '../utils/teamColors';
import { formatDate, formatProbability, ordinal, isPast } from '../utils/format';

// Medal color for top 3 finishers
function positionColor(pos: number) {
    if (pos === 1) return 'var(--accent-gold)';
    if (pos === 2) return 'var(--accent-silver)';
    if (pos === 3) return 'var(--accent-bronze)';
    return 'var(--text-muted)';
}

type SortKey = 'predicted_finish' | 'win_probability' | 'podium_probability' | 'qualifying_position';

export function PredictionsPage() {
    const [selectedKey, setSelectedKey] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState<SortKey>('win_probability');

    // Race list
    const { data: races, isLoading: racesLoading, error: racesError } = useQuery({
        queryKey: ['prediction-races'],
        queryFn: api.getPredictionRaces,
        staleTime: 5 * 60_000,
        onSuccess: (data) => {
            if (!selectedKey && data.length > 0) {
                // Auto-select most recent race with predictions
                const withPreds = data.filter((r) => r.has_predictions);
                if (withPreds.length > 0) {
                    const sorted = [...withPreds].sort((a, b) =>
                        new Date(b.race_date).getTime() - new Date(a.race_date).getTime()
                    );
                    setSelectedKey(sorted[0].race_key);
                }
            }
        },
    } as any);

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
            if (sortBy === 'predicted_finish') return a.predicted_finish - b.predicted_finish;
            if (sortBy === 'qualifying_position') return a.qualifying_position - b.qualifying_position;
            return (b[sortBy] as number) - (a[sortBy] as number);
        });
        return list;
    }, [raceData, sortBy]);

    const isCompleted = raceData?.race_date ? isPast(raceData.race_date) : false;

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

                {/* Race header */}
                {raceData && (
                    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-6 animate-fade-in-up">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span
                                    className="font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm"
                                    style={{
                                        background: isCompleted ? 'var(--bg-elevated)' : 'var(--accent-red)20',
                                        color: isCompleted ? 'var(--text-muted)' : 'var(--accent-red)',
                                        border: `1px solid ${isCompleted ? 'var(--border-default)' : 'var(--accent-red)40'}`,
                                    }}
                                >
                                    {isCompleted ? 'Completed' : 'Upcoming'}
                                </span>
                                <span className="font-mono text-[10px] text-[var(--text-muted)]">
                                    Round {raceData.round} · {raceData.season}
                                </span>
                            </div>
                            <h1 className="font-display font-bold text-2xl sm:text-3xl text-[var(--text-primary)] tracking-wide">
                                {raceData.race_name}
                            </h1>
                            <p className="font-mono text-xs text-[var(--text-muted)] mt-0.5">
                                {formatDate(raceData.race_date)} · Model generated {formatDate(raceData.generated_at)}
                            </p>
                        </div>

                        {/* Sort selector */}
                        <div className="flex items-center gap-1">
                            {(
                                [
                                    { key: 'win_probability', label: 'Win %' },
                                    { key: 'podium_probability', label: 'Podium %' },
                                    { key: 'predicted_finish', label: 'Pred. Pos' },
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

                {/* Prediction table */}
                {predLoading ? (
                    <LoadingState label="Fetching predictions…" />
                ) : predError ? (
                    <ErrorState error={predError as Error} />
                ) : sorted.length === 0 ? (
                    <EmptyState label="No predictions for this race" />
                ) : (
                    <div className="flex flex-col gap-px row-stagger">
                        {/* Column headers */}
                        <div
                            className="hidden sm:grid text-[10px] font-mono uppercase tracking-widest text-[var(--text-muted)] px-3 pb-2"
                            style={{ gridTemplateColumns: '2rem 1fr 6rem 1fr 1fr 4rem' }}
                        >
                            <span>#</span>
                            <span>Driver</span>
                            <span>Team</span>
                            <span>Win prob</span>
                            <span>Podium prob</span>
                            <span className="text-right">
                                {isCompleted ? 'Result' : 'Grid'}
                            </span>
                        </div>

                        {sorted.map((p, idx) => {
                            const theme = getTeamTheme(p.team_id);
                            const showActual = isCompleted && p.actual_finish != null;

                            return (
                                <div
                                    key={p.driver_code}
                                    className="flex sm:grid items-center gap-3 sm:gap-0 px-3 py-3 rounded-sm"
                                    style={{
                                        gridTemplateColumns: '2rem 1fr 6rem 1fr 1fr 4rem',
                                        background: 'var(--bg-surface)',
                                        border: '1px solid var(--border-subtle)',
                                    }}
                                >
                                    {/* Team color accent (mobile) */}
                                    <TeamAccent teamId={p.team_id} />

                                    {/* Rank */}
                                    <span
                                        className="font-display font-bold text-base w-8 shrink-0"
                                        style={{ color: positionColor(idx + 1) }}
                                    >
                                        {idx + 1}
                                    </span>

                                    {/* Driver */}
                                    <div className="flex-1 min-w-0">
                                        <div className="font-display font-bold text-sm text-[var(--text-primary)] leading-tight">
                                            {p.driver_name ?? p.driver_code}
                                        </div>
                                        <div className="font-mono text-[10px] text-[var(--text-muted)]">
                                            {p.driver_code}
                                        </div>
                                    </div>

                                    {/* Team badge */}
                                    <div className="hidden sm:flex">
                                        <TeamBadge teamId={p.team_id} size="sm" />
                                    </div>

                                    {/* Win probability */}
                                    <div className="hidden sm:block pr-4">
                                        <ProbabilityBar value={p.win_probability} color={theme.primary} height={4} />
                                    </div>

                                    {/* Podium probability */}
                                    <div className="hidden sm:block pr-4">
                                        <ProbabilityBar value={p.podium_probability} color={theme.primary} height={4} />
                                    </div>

                                    {/* Mobile probability summary */}
                                    <div className="flex-1 flex flex-col gap-1 sm:hidden">
                                        <div className="flex items-center gap-1">
                                            <span className="font-mono text-[9px] text-[var(--text-muted)] w-8">WIN</span>
                                            <ProbabilityBar value={p.win_probability} color={theme.primary} height={3} />
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <span className="font-mono text-[9px] text-[var(--text-muted)] w-8">POD</span>
                                            <ProbabilityBar value={p.podium_probability} color={theme.primary} height={3} />
                                        </div>
                                    </div>

                                    {/* Result / Grid */}
                                    <div className="text-right shrink-0">
                                        {showActual ? (
                                            <span
                                                className="font-display font-bold text-base"
                                                style={{ color: positionColor(p.actual_finish!) }}
                                            >
                                                {ordinal(p.actual_finish!)}
                                            </span>
                                        ) : (
                                            <span className="font-mono text-xs text-[var(--text-muted)]">
                                                P{p.qualifying_position}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}