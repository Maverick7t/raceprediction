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
        1: "h-[400px]",
        2: "h-[350px]",
        3: "h-[300px]",
    };

    return (
        <div
            className={`
                relative
                overflow-hidden
                rounded-2xl
                w-full
                ${heights[position]}
            `}
            style={{
                backgroundColor: teamColor,
            }}
        >
            {/* F1 Arrow Halftone Pattern */}
            <div
                className="absolute inset-y-0 left-0 w-[75%]"
                style={{
                    background: "rgba(255,255,255,.30)",
                    clipPath:
                        "polygon(0 0, 78% 0, 100% 50%, 78% 100%, 0 100%)",
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
                className="absolute -right-16 top-0 h-full w-80 blur-[120px] opacity-60"
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
                    bottom-[-120px]
                    right-[-10px]
                    h-[115%] 
                    xl:h-[130%]
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
                                fontFamily: "KHInterferenceF1",
                                fontSize: "28px",
                                fontWeight: 700,
                            }}
                        >
                            {position}
                        </span>

                        <span
                            style={{
                                fontFamily: "KHInterferenceF1",
                                fontSize: "12px",
                                fontWeight: 700,
                                marginTop: "2px",
                            }}
                        >
                            {getOrdinalSuffix(position)}
                        </span>
                    </div>

                    {/* Driver Name */}
                    <div className="mt-4 flex flex-col leading-[1.2]">
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
                            fontFamily: "KHInterferenceF1",
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