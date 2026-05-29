// src/components/shared/States.tsx
// Reusable loading skeleton and error state components.

interface SkeletonProps {
    rows?: number;
    className?: string;
}

export function SkeletonRow({ className = '' }: { className?: string }) {
    return (
        <div
            className={`animate-pulse rounded bg-white/5 ${className}`}
            aria-hidden="true"
        />
    );
}

export function PredictionSkeleton({ rows = 10 }: SkeletonProps) {
    return (
        <div className="space-y-2" aria-label="Loading predictions…">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 rounded-lg border border-border-subtle p-4">
                    <SkeletonRow className="h-6 w-8" />
                    <SkeletonRow className="h-4 w-24" />
                    <SkeletonRow className="h-4 flex-1" />
                    <SkeletonRow className="h-4 w-16" />
                    <SkeletonRow className="h-4 w-16" />
                </div>
            ))}
        </div>
    );
}

export function StandingsSkeleton({ rows = 20 }: SkeletonProps) {
    return (
        <div className="space-y-2" aria-label="Loading standings…">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 rounded-lg border border-border-subtle p-3">
                    <SkeletonRow className="h-5 w-6" />
                    <SkeletonRow className="h-4 w-28" />
                    <SkeletonRow className="h-4 flex-1" />
                    <SkeletonRow className="h-4 w-14" />
                </div>
            ))}
        </div>
    );
}

interface ErrorStateProps {
    message?: string;
    onRetry?: () => void;
}

export function ErrorState({
    message = 'Failed to load data.',
    onRetry,
}: ErrorStateProps) {
    return (
        <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-red-500/20 bg-red-500/5 py-16 text-center">
            <div className="font-heading text-4xl text-red-500/40">!</div>
            <p className="font-body text-sm text-text-secondary">{message}</p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="rounded border border-border-default px-4 py-1.5 font-body text-xs text-text-secondary transition hover:border-border-strong hover:text-text-primary"
                >
                    Retry
                </button>
            )}
        </div>
    );
}

export function EmptyState({ message = 'No data available.' }: { message?: string }) {
    return (
        <div className="flex items-center justify-center rounded-lg border border-border-subtle py-16">
            <p className="font-body text-sm text-text-muted">{message}</p>
        </div>
    );
}