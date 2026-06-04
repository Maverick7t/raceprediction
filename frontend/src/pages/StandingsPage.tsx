import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { DriverStandingCard } from '../components/DriverStandingCard';
import { ConstructorStandingCard } from '../components/ConstructorStandingCard';
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
            <div className="mb-6">
                <h1 className="font-apax-th-superbold text-2xl sm:text-3xl tracking-wide uppercase">
                    Championship
                </h1>

                <p className="font-f1 text-[10px] text-[var(--text-muted)] mt-0.5">
                    Season {resolvedYear}
                </p>
            </div>

            {/* Tabs + Years */}
            <div
                className="flex items-end justify-between mb-6"
                style={{
                    borderBottom: '1px solid var(--border-default)',
                }}
            >
                <div className="flex">
                    {(['drivers', 'constructors'] as Tab[]).map((t) => (
                        <button
                            key={t}
                            onClick={() => setTab(t)}
                            className={`
                    px-4
                    py-2.5
                    font-display
                    font-semibold
                    text-sm
                    uppercase
                    tracking-widest
                    transition-colors
                    border-b-2
                    -mb-px
                    ${tab === t
                                    ? 'border-[var(--accent-red)] text-[var(--text-primary)]'
                                    : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                }
                `}
                        >
                            {t}
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-1">
                    {years.map((y) => {
                        const active = (year ?? resolvedYear) === y;

                        return (
                            <button
                                key={y}
                                onClick={() => setYear(y)}
                                className={`
                        relative
                        px-3
                        py-2
                        text-[11px]
                        uppercase
                        transition-all
                        duration-200
                        ${active
                                        ? 'font-f1-bold text-white'
                                        : 'font-f1 text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                    }
                    `}
                            >
                                {y}

                                {active && (
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
                        );
                    })}
                </div>
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
                <div
                    className="
        grid
        grid-cols-1
        xl:grid-cols-2
        gap-5
        row-stagger
    "
                >
                    {constructors.map((constructor) => (
                        <ConstructorStandingCard
                            key={constructor.team_id}
                            position={constructor.position}
                            teamId={constructor.team_id}
                            teamName={constructor.team}
                            points={constructor.points}
                            wins={constructor.wins}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}