function getOrdinalSuffix(position: number) {
    if (position === 1) return "ST";
    if (position === 2) return "ND";
    if (position === 3) return "RD";
    return "TH";
}

type PodiumCardProps = {
    position: 1 | 2 | 3;
    firstName: string;
    lastName: string;
    teamName: string;
    value: string;
    teamColor: string;
    image: string;
};

export function PodiumCard({
    position,
    firstName,
    lastName,
    teamName,
    value,
    teamColor,
    image,
}: PodiumCardProps) {
    const heights = {
        1: "h-[420px]",
        2: "h-[360px]",
        3: "h-[320px]",
    };

    return (
        <div
            className={`
                relative
                overflow-hidden
                rounded-2xl
                ${heights[position]}
            `}
            style={{
                backgroundColor: teamColor,
            }}
        >
            {/* Dot pattern */}
            <div
                className="absolute inset-0 opacity-25"
                style={{
                    backgroundImage:
                        "radial-gradient(rgba(255,255,255,0.9) 1px, transparent 1px)",
                    backgroundSize: "6px 6px",
                }}
            />

            {/* Dark gradient */}
            <div
                className="absolute inset-0"
                style={{
                    background:
                        "linear-gradient(90deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,.15) 35%, rgba(0,0,0,0) 100%)",
                }}
            />

            {/* Team glow */}
            <div
                className="absolute -right-20 top-0 h-full w-64 blur-3xl opacity-40"
                style={{
                    background: teamColor,
                }}
            />

            {/* Driver image */}
            <img
                src={image}
                alt={`${firstName} ${lastName}`}
                style={{ zIndex: 1 }}
                className="
                    absolute
                    bottom-[-140px]
                    right-[-10px]
                    h-[120%]
                    max-w-none
                    object-contain
                    pointer-events-none
                "
            />

            {/* Content */}
            <div className="relative z-20 flex h-full flex-col p-6">
                <div>
                    {/* Position */}
                    <div className="flex items-start gap-2 text-white">
                        <span
                            style={{
                                fontFamily: "KH Interference F1",
                                fontWeight: 700,
                            }}
                        >
                            {position}
                        </span>

                        <span
                            style={{
                                fontFamily: "KH Interference F1",
                                fontSize: "18px",
                                fontWeight: 700,
                                marginTop: "2px",
                            }}
                        >
                            {getOrdinalSuffix(position)}
                        </span>
                    </div>

                    {/* Driver Name */}
                    <div className="mt-4 flex flex-col leading-[0.9]">
                        <span
                            className="text-white"
                            style={{
                                fontFamily: "Formula1R",
                                fontSize: "14px",
                                fontWeight: 200,
                            }}
                        >
                            {firstName}
                        </span>

                        <span
                            className="text-white"
                            style={{
                                fontFamily: "Formula1B",
                                fontSize: "22px",
                                fontWeight: 500,
                            }}
                        >
                            {lastName}
                        </span>
                    </div>

                    {/* Team */}
                    <p
                        className="mt-3 text-white/90"
                        style={{
                            fontFamily: "Formula1R",
                            fontSize: "16px",
                            fontWeight: 10,
                        }}
                    >
                        {teamName}
                    </p>
                </div>

                {/* Probability / Points */}
                <div className="mt-auto">
                    <div
                        style={{
                            fontFamily: "KH Interference F1",
                            fontWeight: 700,
                        }}
                    >
                        {value}

                    </div>
                </div>
            </div>
        </div >
    );
}