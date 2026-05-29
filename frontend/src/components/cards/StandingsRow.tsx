import type { ConstructorStanding, DriverStanding } from '@/types';

type DriverStandingsRowProps = {
    standing: DriverStanding;
    maxPoints: number;
};

type ConstructorStandingsRowProps = {
    standing: ConstructorStanding;
    maxPoints: number;
};

export function DriverStandingsRow({ standing, maxPoints }: DriverStandingsRowProps) {
    const relative = `${Math.round((standing.points / maxPoints) * 100)}%`;

    return (
        <div className="flex items-center gap-3 rounded-lg border border-border-subtle bg-white/3 px-4 py-3">
            <span className="w-7 text-center font-mono text-sm text-text-muted">{standing.position}</span>
            <div className="flex-1 min-w-0">
                <p className="truncate font-body text-sm font-600 text-text-primary">
                    {standing.driver_name}
                </p>
                <p className="truncate font-mono text-xs uppercase tracking-wide text-text-muted">
                    {standing.driver_code} · {standing.team}
                </p>
            </div>
            <span className="hidden w-28 text-sm text-text-muted md:block">{relative}</span>
            <span className="w-6 text-center font-mono text-sm text-text-secondary">{standing.wins}</span>
            <span className="w-14 text-right font-mono text-sm text-text-primary">{standing.points}</span>
        </div>
    );
}

export function ConstructorStandingsRow({ standing, maxPoints }: ConstructorStandingsRowProps) {
    const relative = `${Math.round((standing.points / maxPoints) * 100)}%`;

    return (
        <div className="flex items-center gap-3 rounded-lg border border-border-subtle bg-white/3 px-4 py-3">
            <span className="w-7 text-center font-mono text-sm text-text-muted">{standing.position}</span>
            <div className="flex-1 min-w-0">
                <p className="truncate font-body text-sm font-600 text-text-primary">
                    {standing.team}
                </p>
                <p className="truncate font-mono text-xs uppercase tracking-wide text-text-muted">
                    {standing.team_id}
                </p>
            </div>
            <span className="hidden w-28 text-sm text-text-muted md:block">{relative}</span>
            <span className="w-6 text-center font-mono text-sm text-text-secondary">{standing.wins}</span>
            <span className="w-14 text-right font-mono text-sm text-text-primary">{standing.points}</span>
        </div>
    );
}
