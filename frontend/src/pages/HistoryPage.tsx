import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { RaceListItem } from '../types/api';
import { TeamBadge } from '../components/TeamBadge';
import { ProbabilityBar } from '../components/ProbabilityBar';
import { LoadingState, ErrorState, EmptyState } from '../components/LoadingError';
import { getTeamTheme } from '../utils/teamColors';
import { ordinal } from '../utils/format';

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = [CURRENT_YEAR, CURRENT_YEAR - 1, CURRENT_YEAR - 2];

// Expandable row that fetches prediction data on open
function RaceRow({ race }: { race: RaceListItem }) {
    const [open, setOpen] = useState(false);

    const { data, isLoading, error } = useQuery({
        queryKey: ['predictions', race.race_key],
        queryFn: () => api.getPredictions(race.race_key),
        enabled: open,
        staleTime: 60 * 60_000, // completed races never change
    });

    return (
        <div style={{ border: '1px solid var(--border-subtle)', borderRadius: '2px' }}>
            {/* Row header */}
            <button
                onClick={() => setOpen((v) => !v)}
                className="w-full flex items-center gap-3 px-3 py-3 text-left transition-colors hover:bg-white/5"
                style={{ background: 'var(--bg-surface)' }}
            >
                {/* Round */}
                <div className="flex items-center gap-2 w-20 shrink-0">
                    <span className="font-mono text-[10px] text-[var(--text-muted)]">{race.year}</span>
                    <span className="font-mono text-[10px] text-[var(--text-muted)]">R{race.round}</span>
                </div>

                {/* Race name */}
                <div className="flex-1 min-w-0">
                    <div className="font-display font-semibold text-sm text-[var(--text-primary)] truncate">
                        {race.race_name}
                    </div>
                    <div className="font-mono text-[10px] text-[var(--text-muted)]">
                        {race.circuit_id}
                    </div>
                </div>

                {/* Has predictions badge */}
                {race.has_predictions && (
                    <span
                        className="font-mono text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-sm shrink-0"
                        style={{
                            background: 'var(--bg-elevated)',
                            border: '1px solid var(--border-default)',
                            color: 'var(--text-muted)',
                        }}
                    >
                        Predictions
                    </span>
                )}

                {/* Chevron */}
                <svg
                    className="shrink-0 transition-transform duration-200"
                    style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}
                    width="14" height="14" viewBox="0 0 24 24" fill="none"
                    stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                >
                    <polyline points="6 9 12 15 18 9" />
                </svg>
            </button>

            {/* Expanded predictions */}
            {open && (
                <div
                    className="border-t"
                    style={{ borderColor: 'var(--border-subtle)', background: 'var(--bg-base)' }}
                >
                    {isLoading ? (
                        <LoadingState label="Loading predictions…" />
                    ) : error ? (
                        <ErrorState error={error as Error} />
                    ) : !data?.predictions?.length ? (
                        <EmptyState label="No predictions stored" />
                    ) : (
                        <div className="flex flex-col gap-px p-2">
                            <div className="flex items-center justify-between px-2 pb-1 text-[9px] font-mono uppercase tracking-widest text-[var(--text-muted)]">
                                <span>{data.model_version}</span>
                                <span>{data.generated_at}</span>
                            </div>

                            {[...data.predictions]
                                .sort((a, b) => a.predicted_rank - b.predicted_rank)
                                .map((p, i) => {
                                    const theme = getTeamTheme(p.team_id);

                                    return (
                                        <div
                                            key={p.driver_code}
                                            className="flex sm:grid items-center gap-2 px-2 py-2 rounded-sm"
                                            style={{
                                                gridTemplateColumns: '1.5rem 1fr 5rem 1fr 1fr 3rem 4rem',
                                                background: i % 2 === 0 ? 'var(--bg-surface)' : 'transparent',
                                            }}
                                        >
                                            {/* Team accent */}
                                            <div
                                                className="w-0.5 self-stretch rounded-full shrink-0"
                                                style={{ background: theme.primary }}
                                            />

                                            {/* Driver */}
                                            <div className="flex-1 min-w-0">
                                                <div className="font-display font-semibold text-xs text-[var(--text-primary)] truncate">
                                                    {p.driver_name ?? p.driver_code}
                                                </div>
                                            </div>

                                            {/* Team */}
                                            <div className="hidden sm:flex">
                                                <TeamBadge teamId={p.team_id} size="sm" />
                                            </div>

                                            {/* Win bar */}
                                            <div className="hidden sm:block pr-3">
                                                <ProbabilityBar value={p.predicted_winner_prob} color={theme.primary} height={3} />
                                            </div>

                                            {/* Podium bar */}
                                            <div className="hidden sm:block pr-3">
                                                <ProbabilityBar value={p.predicted_podium_prob} color={theme.primary} height={3} />
                                            </div>

                                            {/* Predicted rank */}
                                            <div className="font-mono text-[10px] text-[var(--text-muted)] text-right shrink-0">
                                                {ordinal(p.predicted_rank)}
                                            </div>

                                            {/* Qualifying position */}
                                            <div className="text-right shrink-0">
                                                <span className="font-mono text-[10px] text-[var(--text-muted)]">
                                                    Q{p.qualifying_position ?? '—'}
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export function HistoryPage() {
    const [year, setYear] = useState(CURRENT_YEAR);

    const { data: races, isLoading, error } = useQuery({
        queryKey: ['races-all'],
        queryFn: api.getRaces,
        staleTime: 30 * 60_000,
    });

    const filtered = (races ?? [])
        .filter((r) => {
            return r.year === year;
        })
        .sort((a, b) => b.round - a.round);

    return (
        <div className="max-w-[1600px] mx-auto w-full px-4 md:px-6 xl:px-10 py-6">

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
                <div>
                    <h1 className="font-display font-bold text-2xl sm:text-3xl text-[var(--text-primary)] tracking-wide">
                        Prediction History
                    </h1>
                    <p className="font-mono text-[10px] text-[var(--text-muted)] mt-0.5">
                        Click a race to see stored prediction snapshots
                    </p>
                </div>

                {/* Year picker */}
                <div className="flex gap-1">
                    {YEARS.map((y) => (
                        <button
                            key={y}
                            onClick={() => setYear(y)}
                            className={`px-3 py-1.5 text-xs font-mono rounded-sm border transition-colors ${year === y
                                ? 'border-[var(--accent-red)] text-[var(--accent-red)] bg-[var(--accent-red)]/10'
                                : 'border-[var(--border-default)] text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                }`}
                        >
                            {y}
                        </button>
                    ))}
                </div>
            </div>

            {/* Race list */}
            {isLoading ? (
                <LoadingState label="Loading race history…" />
            ) : error ? (
                <ErrorState error={error as Error} />
            ) : filtered.length === 0 ? (
                <EmptyState label={`No races found for ${year}`} />
            ) : (
                <div className="flex flex-col gap-1">
                    {filtered.map((race) => (
                        <RaceRow key={race.race_key} race={race} />
                    ))}
                </div>
            )}
        </div>
    );
}