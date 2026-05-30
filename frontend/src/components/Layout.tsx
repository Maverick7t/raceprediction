import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

// Icons (inline SVG to avoid icon library dep)
const IconPredictions = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
);

const IconStandings = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
    </svg>
);

const IconHistory = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
);

const NAV = [
    { to: '/predictions', label: 'Predictions', Icon: IconPredictions },
    { to: '/standings', label: 'Standings', Icon: IconStandings },
    { to: '/history', label: 'History', Icon: IconHistory },
];

function HealthDot() {
    const { data } = useQuery({
        queryKey: ['health'],
        queryFn: api.getHealth,
        refetchInterval: 30_000,
        retry: false,
    });

    const ok = data?.status === 'ok';

    return (
        <div className="flex items-center gap-1.5">
            <div
                className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-emerald-500 animate-pulse-dot' : 'bg-[var(--accent-red)]'}`}
                title={`API ${data?.status ?? 'unknown'}`}
            />
            <span className="font-mono text-[10px] text-[var(--text-muted)] hidden sm:block uppercase tracking-widest">
                {data?.status ?? '…'}
            </span>
        </div>
    );
}

export function Layout() {
    const loc = useLocation();

    return (
        <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-base)' }}>

            {/* ── Top header ─────────────────────────────── */}
            <header
                className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 sm:px-6"
                style={{
                    height: '52px',
                    background: 'var(--bg-surface)',
                    borderBottom: '1px solid var(--border-default)',
                }}
            >
                {/* Logo */}
                <div className="flex items-center gap-2">
                    <div
                        className="w-6 h-6 rounded-sm flex items-center justify-center"
                        style={{ background: 'var(--accent-red)' }}
                    >
                        <span className="font-display font-black text-white text-xs leading-none">F1</span>
                    </div>
                    <span className="font-display font-bold text-sm tracking-widest text-[var(--text-primary)] uppercase">
                        PitWall
                    </span>
                </div>

                {/* Desktop nav */}
                <nav className="hidden sm:flex items-center gap-1">
                    {NAV.map(({ to, label, Icon }) => {
                        const active = loc.pathname.startsWith(to);
                        return (
                            <NavLink
                                key={to}
                                to={to}
                                className={`flex items-center gap-2 px-3 py-1.5 rounded-sm text-xs font-display font-semibold uppercase tracking-widest transition-colors ${active
                                    ? 'text-[var(--accent-red)] bg-[var(--accent-red)]/10'
                                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                                    }`}
                            >
                                <Icon />
                                {label}
                            </NavLink>
                        );
                    })}
                </nav>

                {/* Health */}
                <HealthDot />
            </header>

            {/* ── Page content ───────────────────────────── */}
            <main
                className="flex-1 pb-20 sm:pb-0"
                style={{ marginTop: '52px' }}
            >
                <Outlet />
            </main>

            {/* ── Mobile bottom tab bar ──────────────────── */}
            <nav
                className="sm:hidden fixed bottom-0 left-0 right-0 flex items-center z-50"
                style={{
                    background: 'var(--bg-surface)',
                    borderTop: '1px solid var(--border-default)',
                    height: '56px',
                }}
            >
                {NAV.map(({ to, label, Icon }) => {
                    const active = loc.pathname.startsWith(to);
                    return (
                        <NavLink
                            key={to}
                            to={to}
                            className={`flex-1 flex flex-col items-center justify-center gap-1 h-full transition-colors ${active ? 'text-[var(--accent-red)]' : 'text-[var(--text-muted)]'
                                }`}
                        >
                            <Icon />
                            <span className="font-display font-semibold text-[9px] uppercase tracking-widest">
                                {label}
                            </span>
                        </NavLink>
                    );
                })}
            </nav>

        </div>
    );
}