// LoadingState, ErrorState, EmptyState — shared UI primitives

interface LoadingStateProps {
    label?: string;
}

export function LoadingState({ label = 'Loading...' }: LoadingStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div
                className="w-8 h-8 rounded-full border-2 border-[var(--border-default)] border-t-[var(--accent-red)]"
                style={{ animation: 'spin 0.8s linear infinite' }}
            />
            <p className="font-mono text-xs text-[var(--text-muted)] tracking-widest uppercase">
                {label}
            </p>
        </div>
    );
}

interface ErrorStateProps {
    error: Error | null;
    onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="text-[var(--accent-red)] text-3xl font-display font-bold tracking-widest">
                ERR
            </div>
            <p className="font-mono text-xs text-[var(--text-secondary)] max-w-xs text-center">
                {error?.message ?? 'Unknown error'}
            </p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="mt-2 px-5 py-2 text-xs font-mono uppercase tracking-widest border border-[var(--border-default)] text-[var(--text-secondary)] hover:border-[var(--accent-red)] hover:text-[var(--text-primary)] transition-colors rounded-sm"
                >
                    Retry
                </button>
            )}
        </div>
    );
}

interface EmptyStateProps {
    label?: string;
}

export function EmptyState({ label = 'No data available' }: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-24 gap-3">
            <div className="w-10 h-px bg-[var(--border-default)]" />
            <p className="font-mono text-xs text-[var(--text-muted)] tracking-widest uppercase">
                {label}
            </p>
        </div>
    );
}