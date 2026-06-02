export function HeaderBanner() {
    return (
        <div className="relative h-[220px] w-full overflow-hidden">
            <img
                src="/banner.png"
                alt="F1 Banner"
                className="absolute inset-0 h-full w-full object-cover"
            />

            <div className="absolute inset-0 bg-black/55" />

            <div className="absolute inset-0 flex flex-col justify-center px-8 md:px-16">
                <h1 className="font-display text-4xl md:text-6xl font-bold tracking-wider text-white">
                    F1 PREDICTIONS
                </h1>

                <p className="mt-3 font-mono text-sm md:text-base text-slate-300">
                    AI Race Forecasting
                </p>
            </div>
        </div>
    );
}