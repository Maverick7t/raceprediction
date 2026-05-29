// src/components/layout/StatusBanner.tsx
// Shows a non-blocking warning banner when the prediction data is stale
// (no qualifying data for >10 days). Does not block the UI.

import { useSystemHealth } from '@/hooks/useF1Data';

export function StatusBanner() {
    const { predictionsStale, isLoading } = useSystemHealth();

    if (isLoading || !predictionsStale) return null;

    return (
        <div className="border-b border-amber-500/20 bg-amber-500/8 px-6 py-2.5">
            <p className="mx-auto max-w-6xl font-body text-xs text-amber-400/80">
                <span className="mr-2 inline-block h-1.5 w-1.5 rounded-full bg-amber-400 align-middle" />
                Predictions may be outdated — next qualifying session data not yet available.
            </p>
        </div>
    );
}