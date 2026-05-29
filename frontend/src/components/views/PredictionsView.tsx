// src/components/views/PredictionsView.tsx
// Main predictions page. Shows the latest race's full driver ranking
// with win probability and podium probability.

import { useState } from 'react';
import { useLatestPredictions, usePredictionRaces, usePredictionsByRace } from '@/hooks/useF1Data';
import { PredictionCard } from '@/components/cards/PredictionCard';
import { PredictionSkeleton, ErrorState, EmptyState } from '@/components/shared/States';
import { formatRaceKey } from '@/types';

export function PredictionsView() {
    const [selectedRace, setSelectedRace] = useState<string | null>(null);

    const { data: races } = usePredictionRaces();
    const latestQuery = useLatestPredictions();
    const selectedQuery = usePredictionsByRace(selectedRace);

    const activeQuery = selectedRace ? selectedQuery : latestQuery;
    const { data, isLoading, isError, refetch } = activeQuery;

    const raceLabel = data?.race_key ? formatRaceKey(data.race_key) : 'Latest Predictions';

    return (
        <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 animate-fade-in">
            <div className="mb-8">
                <div className="mb-1 flex items-center gap-2">
                    <div className="h-px flex-1 bg-gradient-to-r from-f1-red/40 to-transparent" />
                    <span className="font-mono text-xs uppercase tracking-widest text-f1-red">
                        Race Forecast
                    </span>
                </div>
                <h1 className="font-heading text-3xl font-700 uppercase tracking-wider text-text-primary">
                    {raceLabel}
                </h1>
                {data?.generated_at && (
                    <p className="mt-1 font-body text-xs text-text-muted">
                        Generated {new Date(data.generated_at).toLocaleString('en-GB')}
                    </p>
                )}
            </div>

            {races && races.length > 1 && (
                <div className="mb-6 flex flex-wrap gap-2">
                    <button
                        onClick={() => setSelectedRace(null)}
                        className={[
                            'rounded border px-3 py-1 font-body text-xs transition',
                            !selectedRace
                                ? 'border-f1-red/40 bg-f1-red-dim text-f1-red'
                                : 'border-border-subtle text-text-secondary hover:border-border-default hover:text-text-primary',
                        ].join(' ')}
                    >
                        Latest
                    </button>
                    {races.slice(0, 8).map(({ race_key }) => (
                        <button
                            key={race_key}
                            onClick={() => setSelectedRace(race_key)}
                            className={[
                                'rounded border px-3 py-1 font-body text-xs transition',
                                selectedRace === race_key
                                    ? 'border-f1-red/40 bg-f1-red-dim text-f1-red'
                                    : 'border-border-subtle text-text-secondary hover:border-border-default hover:text-text-primary',
                            ].join(' ')}
                        >
                            {formatRaceKey(race_key).replace(/\s\d{4}$/, '')}
                        </button>
                    ))}
                </div>
            )}

            <div className="mb-2 flex items-center gap-4 px-4">
                <span className="w-7 text-center font-body text-[10px] uppercase tracking-widest text-text-muted">
                    #
                </span>
                <span className="flex-1 font-body text-[10px] uppercase tracking-widest text-text-muted">
                    Driver
                </span>
                <span className="hidden w-32 font-body text-[10px] uppercase tracking-widest text-text-muted sm:block">
                    Win probability
                </span>
                <span className="w-20 text-right font-body text-[10px] uppercase tracking-widest text-text-muted">
                    Podium
                </span>
            </div>

            {isLoading && <PredictionSkeleton rows={20} />}

            {isError && (
                <ErrorState
                    message="Could not load predictions. The API may be starting up — try again in a moment."
                    onRetry={() => refetch()}
                />
            )}

            {data && data.predictions.length === 0 && (
                <EmptyState message="No predictions available for this race yet." />
            )}

            {data && data.predictions.length > 0 && (
                <div className="space-y-1.5">
                    {data.predictions.map((pred, i) => (
                        <PredictionCard
                            key={pred.driver_code}
                            prediction={pred}
                            rank={i + 1}
                            style={{ animationDelay: `${i * 30}ms` }}
                        />
                    ))}
                </div>
            )}

            {data && (
                <p className="mt-6 text-center font-body text-xs text-text-muted">
                    Predictions are generated offline after qualifying · XGBoost classifier
                </p>
            )}
        </div>
    );
}