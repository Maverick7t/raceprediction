// src/components/layout/Header.tsx
import { Link, useLocation } from 'react-router-dom';

const NAV = [
    { label: 'Predictions', to: '/' },
    { label: 'Standings', to: '/standings' },
    { label: 'History', to: '/history' },
];

export function Header() {
    const { pathname } = useLocation();

    return (
        <header className="sticky top-0 z-50 border-b border-border-subtle bg-bg-primary/80 backdrop-blur-md">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3 group">
                    <div className="h-7 w-1 rounded-full bg-f1-red transition-all group-hover:h-9" />
                    <span className="font-heading text-xl font-700 tracking-widest text-text-primary uppercase">
                        F1<span className="text-f1-red">.</span>PREDICT
                    </span>
                </Link>

                {/* Nav */}
                <nav className="flex items-center gap-1">
                    {NAV.map(({ label, to }) => {
                        const active = pathname === to;
                        return (
                            <Link
                                key={to}
                                to={to}
                                className={[
                                    'rounded px-4 py-1.5 font-body text-sm font-500 tracking-wide transition-all',
                                    active
                                        ? 'bg-f1-red-dim text-f1-red'
                                        : 'text-text-secondary hover:text-text-primary hover:bg-white/5',
                                ].join(' ')}
                            >
                                {label}
                            </Link>
                        );
                    })}
                </nav>
            </div>
        </header>
    );
}