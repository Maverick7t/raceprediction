/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        colors: {
            transparent: 'transparent',
            current: 'currentColor',
            white: '#ffffff',
            black: '#000000',
            slate: {
                50: '#f8fafc',
                100: '#f1f5f9',
                200: '#e2e8f0',
                300: '#cbd5e1',
                400: '#94a3b8',
                500: '#64748b',
                600: '#475569',
                700: '#334155',
                800: '#1e293b',
                900: '#0f172a',
            },
            cyan: {
                300: '#06b6d4',
                400: '#06b6d4',
                500: '#06b6d4',
            },
            // Core palette
            gold: '#FFD700',
            silver: '#C0C0C0',
            bronze: '#CD7F32',
        },
        fontFamily: {
            display: ['Barlow Condensed', 'sans-serif'],
            barlow: ['Barlow Condensed', 'sans-serif'],
            body: ['Barlow', 'sans-serif'],
            mono: ['DM Mono', 'monospace'],
            heading: ['Rajdhani', 'sans-serif'],
        },
        extend: {
            animation: {
                'fill-bar': 'fillBar 0.8s ease-out forwards',
                'fade-in': 'fadeIn 0.4s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
                'fade-in-up': 'fadeInUp 0.6s ease-out',
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
                fadeInUp: {
                    from: { opacity: '0', transform: 'translateY(16px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
            },
        },
    },
    plugins: [],
}