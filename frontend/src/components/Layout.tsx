import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { HeaderBanner } from './HeaderBanner';

const NAV = [
    { to: '/predictions', label: 'Predictions' },
    { to: '/standings', label: 'Standings' },
    { to: '/history', label: 'History' },
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
                className={`w-1.5 h-1.5 rounded-full ${ok
                    ? 'bg-emerald-500 animate-pulse-dot'
                    : 'bg-[var(--accent-red)]'
                    }`}
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
        <div
            className="min-h-screen flex flex-col"
            style={{ background: 'var(--bg-base)' }}
        >
            <HeaderBanner />

            {/* Top header */}
            <header
                className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 sm:px-6"
                style={{
                    height: '60px',
                    background: 'var(--bg-surface)',
                    borderBottom: '1px solid var(--border-default)',
                }}
            >
                {/* Logo */}
                <div className="flex items-center">
                    <img
                        src="/f1l.png"
                        alt="Formula 1"
                        className="h-12 w-auto object-contain"
                    />
                </div>

                {/* Desktop nav */}
                <nav className="hidden sm:flex items-center gap-6">
                    {NAV.map(({ to, label }) => {
                        const active = loc.pathname.startsWith(to);

                        return (
                            <NavLink
                                key={to}
                                to={to}
                                className={`
                                    relative
                                    px-2
                                    py-5
                                    uppercase
                                    text-xs
                                    tracking-[0.14em]
                                    transition-colors
                                    ${active
                                        ? 'font-f1-bold text-white'
                                        : 'font-f1-bold text-[var(--text-secondary)] hover:text-white'
                                    }
                                `}
                            >
                                {label}

                                {active && (
                                    <span
                                        className="
                                            absolute
                                            left-0
                                            bottom-0
                                            w-full
                                            h-[3px]
                                            bg-[#e10600]
                                        "
                                    />
                                )}
                            </NavLink>
                        );
                    })}
                </nav>

                {/* Health */}
                <HealthDot />
            </header>

            {/* Page content */}
            <main
                className="flex-1 pb-20 sm:pb-0"
                style={{ marginTop: 0 }}
            >
                <Outlet />
            </main>

            {/* Mobile bottom nav */}
            <nav
                className="sm:hidden fixed bottom-0 left-0 right-0 flex items-center z-50"
                style={{
                    background: 'var(--bg-surface)',
                    borderTop: '1px solid var(--border-default)',
                    height: '56px',
                }}
            >
                {NAV.map(({ to, label }) => {
                    const active = loc.pathname.startsWith(to);

                    return (
                        <NavLink
                            key={to}
                            to={to}
                            className="relative flex-1 flex items-center justify-center h-full"
                        >
                            <span
                                className={`
                                    font-f1-bold
                                    text-[9px]
                                    uppercase
                                    tracking-[0.12em]
                                    ${active
                                        ? 'text-white'
                                        : 'text-[var(--text-muted)]'
                                    }
                                `}
                            >
                                {label}
                            </span>

                            {active && (
                                <span
                                    className="
                                        absolute
                                        top-0
                                        left-0
                                        w-full
                                        h-[3px]
                                        bg-[#e10600]
                                    "
                                />
                            )}
                        </NavLink>
                    );
                })}
            </nav>
        </div>
    );
}