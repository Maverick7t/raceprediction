import { getTeamTheme } from '../utils/teamColors';

interface TeamBadgeProps {
    teamId: string;
    size?: 'sm' | 'md';
    className?: string;
}

export function TeamBadge({ teamId, size = 'md', className = '' }: TeamBadgeProps) {
    const theme = getTeamTheme(teamId);
    const isSmall = size === 'sm';

    return (
        <span
            className={`inline-flex items-center rounded-sm font-display font-bold uppercase tracking-wider ${isSmall ? 'text-[9px] px-1.5 py-0.5' : 'text-[11px] px-2 py-1'
                } ${className}`}
            style={{
                background: theme.primary + '26',   // 15% opacity fill
                color: theme.primary,
                border: `1px solid ${theme.primary}40`,
                letterSpacing: '0.1em',
            }}
            title={theme.name}
        >
            {theme.abbrev}
        </span>
    );
}

// Solid left-border accent used in table rows
export function TeamAccent({ teamId }: { teamId: string }) {
    const theme = getTeamTheme(teamId);
    return (
        <div
            className="w-0.5 self-stretch rounded-full shrink-0"
            style={{ background: theme.primary }}
        />
    );
}