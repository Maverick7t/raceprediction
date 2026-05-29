// src/components/views/StandingsView.tsx
// Tabbed page for driver and constructor championship standings.
// Year selector allows viewing historical seasons.

import { useState } from 'react';
import { useDriverStandings, useConstructorStandings } from '@/hooks/useF1Data';
import { DriverStandingsRow, ConstructorStandingsRow } from '@/components/cards/StandingsRow';
import { StandingsSkeleton, ErrorState } from '@/components/shared/States';

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = [CURRENT_YEAR, CURRENT_YEAR - 1, CURRENT_YEAR - 2];

type Tab = 'drivers' | 'constructors';

export function StandingsView() {
    const [tab, setTab] = useState<Tab>('drivers');
    const [year, setYear] = useState(CURRENT_YEAR);

    const drivers = useDriverStandings(year);
    const constructors = useConstructorStandings(year);

    const activeQuery = tab === 'drivers' ? drivers : constructors;

    const driverRows = drivers.data?.standings ?? [];
    const constructorRows = constructors.data?.standings ?? [];
    const maxDriverPts = driverRows[0]?.points ?? 1;
    const maxConstructorPts = constructorRows[0]?.points ?? 1;

    return (
        <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 animate-fade-in">
            {/* Page header */}
            <div className="mb-8">
                <div className="mb-1 flex items-center gap-2">
                    <div className="h-px flex-1 bg-gradient-to-r from-f1-red/40 to-transparent" />
                    <span className="font-mono text-xs uppercase tracking-widest text-f1-red">
                        Championship
                    </span>
                </div>
                <h1 className="font-heading text-3xl font-700 uppercase tracking-wider text-text-primary">
                    {year} Standings
                </h1>
            </div>

            {/* Controls row */}
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
                {/* Tabs */}
                <div className="flex rounded border border-border-subtle p-0.5">
                    {(['drivers', 'constructors'] as Tab[]).map((t) => (
                        <button
                            key={t}
                            onClick={() => setTab(t)}
                            className={[
                                'rounded px-4 py-1.5 font-body text-xs capitalize transition',
                                tab === t
                                    ? 'bg-f1-red-dim text-f1-red'
                                    : 'text-text-secondary hover:text-text-primary',
                            ].join(' ')}
                        >
                            {t}
                        </button>
                    ))}
                </div>

                {/* Year selector */}
                <div className="flex gap-1.5">
                    {YEARS.map((y) => (
                        <button
                            key={y}
                            onClick={() => setYear(y)}
                            className={[
                                'rounded border px-3 py-1 font-mono text-xs transition',
                                year === y
                                    ? 'border-f1-red/40 bg-f1-red-dim text-f1-red'
                                    : 'border-border-subtle text-text-secondary hover:border-border-default hover:text-text-primary',
                            ].join(' ')}
                        >
                            {y}
                        </button>
                    ))}
                </div>
            </div>

            {/* Column headers */}
            <div className="mb-2 flex items-center gap-3 px-4">
                <span className="w-7 text-center font-body text-[10px] uppercase tracking-widest text-text-muted">#</span>
                <span className="flex-1 font-body text-[10px] uppercase tracking-widest text-text-muted">
                    {tab === 'drivers' ? 'Driver' : 'Constructor'}
                </span>
                <span className="hidden w-28 font-body text-[10px] uppercase tracking-widest text-text-muted md:block">
                    Relative
                </span>
                <span className="w-6 text-center font-body text-[10px] uppercase tracking-widest text-text-muted">W</span>
                <span className="w-14 text-right font-body text-[10px] uppercase tracking-widest text-text-muted">PTS</span>
            </div>

            {/* Content */}
            {activeQuery.isLoading && <StandingsSkeleton />}

            {activeQuery.isError && (
                <ErrorState
                    message="Could not load standings."
                    onRetry={() => activeQuery.refetch()}
                />
            )}

            {tab === 'drivers' && !drivers.isLoading && (
                <div className="space-y-1">
                    {driverRows.map((s) => (
                        <DriverStandingsRow key={s.driver_code} standing={s} maxPoints={maxDriverPts} />
                    ))}
                </div>
            )}

            {tab === 'constructors' && !constructors.isLoading && (
                <div className="space-y-1">
                    {constructorRows.map((s) => (
                        <ConstructorStandingsRow key={s.team_id} standing={s} maxPoints={maxConstructorPts} />
                    ))}
                </div>
            )}

            {drivers.data?.updated_at && (
                <p className="mt-6 text-center font-body text-xs text-text-muted">
                    Last synced{' '}
                    {new Date(drivers.data.updated_at).toLocaleDateString('en-GB', {
                        day: 'numeric',
                        month: 'short',
                    })}
                </p>
            )}
        </div>
    );
}