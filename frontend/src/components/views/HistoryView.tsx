// src/components/views/HistoryView.tsx
// Shows all races that have stored predictions, let the user click to see each one.

import { useState } from 'react';
import { usePredictionRaces, usePredictionsByRace } from '@/hooks/useF1Data';
import { PredictionCard } from '@/components/cards/PredictionCard';
import { PredictionSkeleton, ErrorState, EmptyState } from '@/components/shared/States';
import { formatRaceKey } from '@/types';

export function HistoryView() {
    const { data: races, isLoading: racesLoading } = usePredictionRaces();
    const [selected, setSelected] = useState<string | null>(null);
    const { data, isLoading, isError, refetch } = usePredictionsByRace(selected);

    return (
        <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 animate-fade-in">
            {/* Header */}
            <div className="mb-8">
                <div className="mb-1 flex items-center gap-2">
                    <div className="h-px flex-1 bg-gradient-to-r from-f1-red/40 to-transparent" />
                    <span className="font-mono text-xs uppercase tracking-widest text-f1-red">Archive</span>
                </div>
                <h1 className="font-heading text-3xl font-700 uppercase tracking-wider text-text-primary">
                    Race History
                </h1>
            </div>

            <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
                {/* Race list sidebar */}
                <div>
                    <p className="mb-3 font-body text-[10px] uppercase tracking-widest text-text-muted">
                        Select a race
                    </p>
                    {racesLoading && (
                        <div className="space-y-2">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div key={i} className="h-9 animate-pulse rounded bg-white/5" />
                            ))}
                        </div>
                    )}
                    <div className="space-y-1">
                        {(races ?? []).map(({ race_key }) => (
                            <button
                                key={race_key}
                                onClick={() => setSelected(race_key)}
                                className={[
                                    'w-full rounded border px-3 py-2 text-left font-body text-xs transition',
                                    selected === race_key
                                        ? 'border-f1-red/40 bg-f1-red-dim text-f1-red'
                                        : 'border-border-subtle text-text-secondary hover:border-border-default hover:text-text-primary',
                                ].join(' ')}
                            >
                                {formatRaceKey(race_key)}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Prediction detail */}
                <div>
                    {!selected && (
                        <EmptyState message="Select a race from the list to view predictions." />
                    )}

                    {selected && isLoading && <PredictionSkeleton rows={20} />}

                    {selected && isError && (
                        <ErrorState message="Could not load predictions." onRetry={() => refetch()} />
                    )}

                    {data && (
                        <>
                            <p className="mb-4 font-heading text-lg font-600 uppercase tracking-wide text-text-primary">
                                {formatRaceKey(data.race_key)}
                            </p>
                            <div className="space-y-1.5">
                                {data.predictions.map((pred, i) => (
                                    <PredictionCard key={pred.driver_code} prediction={pred} rank={i + 1} />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}