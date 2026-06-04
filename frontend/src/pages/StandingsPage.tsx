import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { TeamBadge } from '../components/TeamBadge';
import { LoadingState, ErrorState } from '../components/LoadingError';
import { getTeamTheme } from '../utils/teamColors';

type Tab = 'drivers' | 'constructors';

// Thin horizontal bar scaled to leader points
function PointsBar({ points, max }: { points: number; max: number }) {
    const pct = max > 0 ? (points / max) * 100 : 0;
    return (
        <div className="flex items-center gap-2 flex-1">
            <div
                className="flex-1 rounded-full overflow-hidden"
                style={{ height: 3, background: 'var(--bg-elevated)' }}
            >
                <div
                    className="h-full rounded-full"
                    style={{
                        width: `${pct}%`,
                        background: 'var(--text-secondary)',
                        transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                />
            </div>
            <span className="font-mono text-xs text-[var(--text-primary)] w-10 text-right">
                {points}
            </span>
        </div>
    );
}

function PositionBadge({ pos }: { pos: number }) {
    const colors: Record<number, string> = {
        1: 'var(--accent-gold)',
        2: 'var(--accent-silver)',
        3: 'var(--accent-bronze)',
    };
    const c = colors[pos] ?? 'var(--text-muted)';
    return (
        <span className="font-display font-bold text-base w-8 shrink-0" style={{ color: c }}>
            {pos}
        </span>
    );
}

export function StandingsPage() {
    const [tab, setTab] = useState<Tab>('drivers');
    const [year, setYear] = useState<number | null>(null);

    const driverQuery = useQuery({
        queryKey: ['standings-drivers', year ?? 'latest'],
        queryFn: () => api.getDriverStandings(year ?? undefined),
        staleTime: 10 * 60_000,
        enabled: tab === 'drivers',
    });

    const constructorQuery = useQuery({
        queryKey: ['standings-constructors', year ?? 'latest'],
        queryFn: () => api.getConstructorStandings(year ?? undefined),
        staleTime: 10 * 60_000,
        enabled: tab === 'constructors',
    });

    const driverData = driverQuery.data;
    const constructorData = constructorQuery.data;
    const resolvedYear = year ?? driverData?.year ?? constructorData?.year ?? new Date().getFullYear();
    const years = [resolvedYear, resolvedYear - 1, resolvedYear - 2];

    const activeQuery = tab === 'drivers' ? driverQuery : constructorQuery;
    const drivers = driverData?.standings ?? [];
    const constructors = constructorData?.standings ?? [];

    const maxDriverPts = Math.max(...drivers.map((d) => d.points), 1);
    const maxConstructorPts = Math.max(...constructors.map((c) => c.points), 1);

    return (
        <div className="max-w-[1600px] mx-auto w-full px-4 md:px-10 py-6">

            {/* Page header */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
                <div>
                    <h1 className="font-apax-th-superbold text-2xl sm:text-3xl tracking-wide uppercase">
                        Championship
                    </h1>
                    <p className="font-f1 text-[10px] text-[var(--text-muted)] mt-0.5">
                        Season {resolvedYear}
                    </p>
                </div>

                {/* Year picker */}
                <div className="flex gap-1">
                    {years.map((y) => (
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

            {/* Tabs */}
            <div
                className="flex mb-6"
                style={{ borderBottom: '1px solid var(--border-default)' }}
            >
                {(['drivers', 'constructors'] as Tab[]).map((t) => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`px-4 py-2.5 font-display font-semibold text-sm uppercase tracking-widest transition-colors border-b-2 -mb-px ${tab === t
                            ? 'border-[var(--accent-red)] text-[var(--text-primary)]'
                            : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                            }`}
                    >
                        {t}
                    </button>
                ))}
            </div>

            {/* Content */}
            {activeQuery.isLoading ? (
                <LoadingState label="Loading standings…" />
            ) : activeQuery.error ? (
                <ErrorState error={activeQuery.error as Error} />
            ) : tab === 'drivers' ? (
                <div className="flex flex-col gap-px row-stagger">
                    {drivers.map((d) => {
                        const theme = getTeamTheme(d.team);
                        return (
                            <div
                                key={d.driver_code}
                                className="flex items-center gap-3 px-3 py-3 rounded-sm"
                                style={{
                                    background: 'var(--bg-surface)',
                                    border: '1px solid var(--border-subtle)',
                                }}
                            >
                                {/* Team accent strip */}
                                <div
                                    className="w-0.5 self-stretch rounded-full shrink-0"
                                    style={{ background: theme.primary }}
                                />

                                <PositionBadge pos={d.position} />

                                {/* Driver info */}
                                <div className="w-58 shrink-0">
                                    <div className="font-f1 text-white truncate tracking-[0.03em]">
                                        {d.driver_name}
                                    </div>
                                    <div className="font-mono text-[10px] text-[var(--text-muted)]">
                                        {d.driver_code}
                                    </div>
                                </div>

                                {/* Team badge */}
                                <TeamBadge teamId={d.team} size="sm" />

                                {/* Points bar */}
                                <PointsBar points={d.points} max={maxDriverPts} />

                                {/* Wins */}
                                <div className="text-right shrink-0 w-12">
                                    <div className="font-mono text-xs text-[var(--text-muted)]">
                                        {d.wins}W
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="flex flex-col gap-px row-stagger">
                    {constructors.map((c) => {
                        const theme = getTeamTheme(c.team_id);
                        return (
                            <div
                                key={c.team_id}
                                className="flex items-center gap-3 px-3 py-3 rounded-sm"
                                style={{
                                    background: 'var(--bg-surface)',
                                    border: '1px solid var(--border-subtle)',
                                }}
                            >
                                <div
                                    className="w-0.5 self-stretch rounded-full shrink-0"
                                    style={{ background: theme.primary }}
                                />
                                <PositionBadge pos={c.position} />
                                <div className="flex-1 min-w-0">
                                    <div className="font-f1 text-white truncate tracking-[0.03em]">
                                        {c.team}
                                    </div>
                                </div>

                                <PointsBar points={c.points} max={maxConstructorPts} />
                                <div className="text-right shrink-0 w-12">
                                    <div className="font-mono text-xs text-[var(--text-muted)]">
                                        {c.wins}W
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}