import { getTeamTheme } from '../utils/teamColors';

interface TeamBadgeProps {
    teamId: string;
    size?: 'sm' | 'md';
    className?: string;
}

export function TeamBadge({
    teamId,
    size = 'md',
    className = '',
}: TeamBadgeProps) {
    const theme = getTeamTheme(teamId);
    const isSmall = size === 'sm';

    return (
        <span
            className={`font-mono uppercase text-slate-500 ${isSmall ? 'text-[16px]' : 'text-[11px]'
                } ${className}`}
            title={theme.name}
        >
            {theme.abbrev}
        </span>
    );
}

export function TeamAccent() {
    return null;
}