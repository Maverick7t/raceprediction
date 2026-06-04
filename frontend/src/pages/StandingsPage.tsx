import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { DriverStandingCard } from '../components/DriverStandingCard';
import { LoadingState, ErrorState } from '../components/LoadingError';
import { getTeamTheme } from '../utils/teamColors';

type Tab = 'drivers' | 'constructors';

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

    const resolvedYear =
        year ??
        driverData?.year ??
        constructorData?.year ??
        new Date().getFullYear();

    const years = [
        resolvedYear,
        resolvedYear - 1,
        resolvedYear - 2,
    ];

    const activeQuery =
        tab === 'drivers'
            ? driverQuery
            : constructorQuery;

    const drivers = driverData?.standings ?? [];
    const constructors = constructorData?.standings ?? [];

    return (
        <div className="max-w-[1600px] mx-auto w-full px-4 md:px-10 py-6">

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
                <div>
                    <h1 className="font-apax-th-superbold text-2xl sm:text-3xl tracking-wide uppercase">
                        Championship
                    </h1>

                    <p className="font-f1 text-[10px] text-[var(--text-muted)] mt-0.5">
                        Season {resolvedYear}
                    </p>
                </div>

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
                style={{
                    borderBottom: '1px solid var(--border-default)',
                }}
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

                <div
                    className="
                        grid
                        grid-cols-1
                        xl:grid-cols-2
                        gap-5
                        row-stagger
                    "
                >
                    {drivers.map((driver) => (
                        <DriverStandingCard
                            key={driver.driver_code}
                            position={driver.position}
                            driverName={driver.driver_name}
                            driverCode={driver.driver_code}
                            team={driver.team}
                            points={driver.points}
                            wins={driver.wins}
                        />
                    ))}
                </div>

            ) : (

                <div className="flex flex-col gap-3">
                    {constructors.map((c) => {
                        const theme = getTeamTheme(c.team_id);

                        return (
                            <div
                                key={c.team_id}
                                className="flex items-center gap-4 px-4 py-4 rounded-xl"
                                style={{
                                    background: 'var(--bg-surface)',
                                    border:
                                        '1px solid var(--border-subtle)',
                                }}
                            >
                                <div
                                    className="w-1 self-stretch rounded-full shrink-0"
                                    style={{
                                        background: theme.primary,
                                    }}
                                />

                                <div
                                    className="font-bold text-lg w-10 shrink-0"
                                    style={{
                                        color: theme.primary,
                                    }}
                                >
                                    P{c.position}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="font-f1 text-white truncate">
                                        {c.team}
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div
                                        className="text-white"
                                        style={{
                                            fontFamily:
                                                'KHInterferenceF1',
                                            fontSize: '32px',
                                        }}
                                    >
                                        {c.points}
                                    </div>

                                    <div className="font-f1 text-[10px] text-[var(--text-muted)]">
                                        POINTS
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