import type { CSSProperties } from 'react';
import { formatPct } from '@/types';
import type { Prediction } from '@/types';

type PredictionCardProps = {
    prediction: Prediction;
    rank: number;
    style?: CSSProperties;
};

export function PredictionCard({ prediction, rank, style }: PredictionCardProps) {
    return (
        <div
            style={style}
            className="flex items-center gap-4 rounded-lg border border-border-subtle bg-white/3 px-4 py-3 transition hover:border-border-default"
        >
            <span className="w-7 text-center font-mono text-sm text-text-muted">{rank}</span>
            <div className="flex-1 min-w-0">
                <p className="truncate font-body text-sm font-600 text-text-primary">
                    {prediction.driver_name}
                </p>
                <p className="truncate font-mono text-xs uppercase tracking-wide text-text-muted">
                    {prediction.driver_code} · {prediction.team_id}
                </p>
            </div>
            <div className="hidden w-32 sm:block">
                <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
                    <div
                        className="h-full rounded-full bg-f1-red"
                        style={{ width: formatPct(prediction.winner_probability) }}
                    />
                </div>
                <p className="mt-1 font-mono text-[11px] text-text-muted">
                    Win {formatPct(prediction.winner_probability)}
                </p>
            </div>
            <div className="w-20 text-right font-mono text-sm text-text-secondary">
                {formatPct(prediction.podium_probability)}
            </div>
        </div>
    );
}