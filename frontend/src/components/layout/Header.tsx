import { Link, useLocation } from 'react-router-dom';

const NAV = [
    { label: 'Predictions', to: '/' },
    { label: 'Standings', to: '/standings' },
    { label: 'History', to: '/history' },
];

export function Header() {
    const { pathname } = useLocation();

    return (
        <header
            className="
                sticky
                top-0
                z-50
                border-b
                border-[var(--border-default)]
                bg-[var(--bg-surface)]/80
                backdrop-blur-md
            "
        >
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

                {/* Logo */}
                <Link
                    to="/"
                    className="group flex items-center gap-4"
                >
                    <div
                        className="
                            h-6
                            w-[2px]
                            bg-white/40
                            transition-all
                            duration-200
                            group-hover:h-8
                        "
                    />

                    <span
                        className="
                            font-f1-bold
                            text-lg
                            uppercase
                            tracking-[0.25em]
                            text-white
                        "
                    >
                        F1.PREDICT
                    </span>
                </Link>

                {/* Navigation */}
                <nav className="flex items-center gap-8">
                    {NAV.map(({ label, to }) => {
                        const active = pathname === to;

                        return (
                            <Link
                                key={to}
                                to={to}
                                className={`
                                    relative
                                    uppercase
                                    text-sm
                                    tracking-[0.18em]
                                    transition-all
                                    duration-200
                                    ${active
                                        ? 'font-f1-bold text-white'
                                        : 'font-f1 text-[var(--text-secondary)] hover:text-white'
                                    }
                                `}
                            >
                                {label}

                                {active && (
                                    <span
                                        className="
                                            absolute
                                            -bottom-2
                                            left-0
                                            w-full
                                            h-[2px]
                                            bg-white
                                        "
                                    />
                                )}
                            </Link>
                        );
                    })}
                </nav>

            </div>
        </header>
    );
}