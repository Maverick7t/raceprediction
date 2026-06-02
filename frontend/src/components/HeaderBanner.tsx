export function HeaderBanner() {
    return (
        <div className="relative h-[220px] w-full overflow-hidden">
            <img
                src="/f1-banner.webp"
                alt="F1 Banner"
                className="absolute inset-0 h-full w-full object-cover"
            />

            <div className="absolute inset-0 bg-black/55" />

            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <h1 className="font-display text-5xl font-bold tracking-widest text-white">
                    F1 PREDICTIONS
                </h1>

                <p className="mt-2 font-mono text-sm text-slate-300">
                    AI-Powered Race Forecasting
                </p>
            </div>
        </div>
    );
}