/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                heading: ['Rajdhani', 'sans-serif'],
                body: ['Outfit', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                // Core palette
                'bg-primary': '#06060A',
                'bg-surface': '#0E0E14',
                'bg-elevated': '#16161E',
                // Borders
                'border-subtle': 'rgba(255,255,255,0.06)',
                'border-default': 'rgba(255,255,255,0.10)',
                'border-strong': 'rgba(255,255,255,0.18)',
                // Text
                'text-primary': '#F0F0F5',
                'text-secondary': '#8888A0',
                'text-muted': '#484858',
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