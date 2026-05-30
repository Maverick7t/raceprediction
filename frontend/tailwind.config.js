/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                display: ['Barlow Condensed', 'sans-serif'],
                body: ['Barlow', 'sans-serif'],
                mono: ['DM Mono', 'monospace'],
                // Keep existing aliases so current components continue to render correctly.
                heading: ['Rajdhani', 'sans-serif'],
            },
            colors: {
                // Core palette
                'bg-primary': '#0B0B0F',
                'bg-surface': '#0E0E14',
                'bg-elevated': '#13131A',
                // Borders
                'border-subtle': 'rgba(255,255,255,0.08)',
                'border-default': 'rgba(255,255,255,0.12)',
                'border-strong': 'rgba(255,255,255,0.20)',
                // Text
                'text-primary': '#F2F2F7',
                'text-secondary': '#A8A8B6',
                'text-muted': '#6B6B7F',
                // Accent
                'f1-red': '#E10600',
                'f1-red-dim': 'rgba(225,6,0,0.15)',
                // Podium
                'gold': '#FFD700',
                'silver': '#C0C0C0',
                'bronze': '#CD7F32',
            },
            animation: {
                'fill-bar': 'fillBar 0.8s ease-out forwards',
                'fade-in': 'fadeIn 0.4s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
            },
            keyframes: {
                fillBar: {
                    from: { width: '0%' },
                    to: { width: 'var(--bar-width)' },
                },
                fadeIn: {
                    from: { opacity: '0' },
                    to: { opacity: '1' },
                },
                slideUp: {
                    from: { opacity: '0', transform: 'translateY(12px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
            },
        },
    },
    plugins: [],
}