import { getTeamTheme } from "../utils/teamColors";

type DriverStandingCardProps = {
    position: number;
    driverName: string;
    driverCode: string;
    team: string;
    points: number;
    wins: number;
};

export function DriverStandingCard({
    position,
    driverName,
    driverCode,
    team,
    points,
    wins,
}: DriverStandingCardProps) {
    const theme = getTeamTheme(team);

    const [firstName, ...rest] = driverName.split(" ");
    const lastName = rest.join(" ");

    return (
        <div
            className="
                relative
                overflow-hidden
                rounded-2xl
                h-[260px]
            "
            style={{
                backgroundColor: theme.primary,
            }}
        >
            {/* Arrow pattern */}
            <div
                className="absolute inset-y-0 left-0 w-[75%]"
                style={{
                    background: "rgba(255,255,255,.20)",
                    clipPath:
                        "polygon(0 0, 78% 0, 100% 50%, 78% 100%, 0 100%)",
                }}
            />

            {/* Dark overlay */}
            <div
                className="absolute inset-0"
                style={{
                    background:
                        "linear-gradient(90deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,.15) 40%, rgba(0,0,0,0) 100%)",
                }}
            />

            {/* Team glow */}
            <div
                className="
                    absolute
                    -right-16
                    top-0
                    h-full
                    w-80
                    blur-[120px]
                    opacity-60
                "
                style={{
                    background: theme.primary,
                }}
            />

            {/* Driver image */}
            <img
                src={`/drivers/${driverCode.toUpperCase()}.png`}
                alt={driverName}
                className="
                    absolute
                    bottom-[-260px]
                    right-[-1px]
                    h-[200%]
                    object-contain
                    pointer-events-none
                "
            />

            {/* Content */}
            <div className="relative z-20 flex h-full flex-col p-6">

                {/* Position */}
                <div
                    className="text-white/90"
                    style={{
                        fontFamily: "KHInterferenceF1",
                        fontSize: "20px",
                    }}
                >
                    P{position}
                </div>

                {/* Driver */}
                <div className="mt-3 max-w-[55%] md:max-w-[60%]">
                    <div
                        className=" text-white text-[14px] md:text-[18px] "
                        style={{
                            fontFamily: "Formula1R",
                        }}
                    >
                        {firstName}
                    </div>

                    <div
                        className=" text-white leading-none text-[20px] md:text-[34px] "
                        style={{
                            fontFamily: "Formula1B",
                        }}
                    >
                        {lastName}
                    </div>

                    <div
                        className="mt-2 text-white/90"
                        style={{
                            fontFamily: "Formula1R",
                            fontSize: "14px",
                        }}
                    >
                        {theme.name}
                    </div>
                </div>

                {/* Stats */}
                <div className="mt-auto flex gap-8">

                    <div>
                        <div
                            className="text-white"
                            style={{
                                fontFamily: "KHInterferenceF1",
                                fontSize: "28px",
                            }}
                        >
                            {points}
                        </div>

                        <div className="font-f1 text-xs text-white/80">
                            POINTS
                        </div>
                    </div>

                    <div>
                        <div
                            className="text-white"
                            style={{
                                fontFamily: "KHInterferenceF1",
                                fontSize: "28px",
                            }}
                        >
                            {wins}
                        </div>

                        <div className="font-f1 text-xs text-white/80">
                            WINS
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}