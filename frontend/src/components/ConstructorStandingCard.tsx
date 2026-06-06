import { getTeamTheme } from '../utils/teamColors';
import { getTeamLogo } from '../utils/teamAssets';

type ConstructorStandingCardProps = {
    position: number;
    teamId: string;
    teamName: string;
    points: number;
    wins: number;
};

export function ConstructorStandingCard({
    position,
    teamId,
    teamName,
    points,
    wins,
}: ConstructorStandingCardProps) {
    const theme = getTeamTheme(teamId);

    return (
        <div
            className="relative overflow-hidden rounded-2xl h-[280px] md:h-[320px]"
            style={{
                background: theme.primary,
            }}
        >
            {/* Dots */}
            <div
                className="absolute inset-0 opacity-20"
                style={{
                    backgroundImage:
                        'radial-gradient(circle, rgba(255,255,255,.8) 1px, transparent 1px)',
                    backgroundSize: '6px 6px',
                }}
            />

            {/* Logo */}
            <div
                className="absolute top-6 right-6 h-10 w-10 md:h-14 md:w-14 rounded-full bg-black/50 flex items-center justify-center backdrop-blur-sm "
            >
                <img
                    src={getTeamLogo(teamId)}
                    alt={teamName}
                    className="h-6 w-6 md:h-8 md:w-8 object-contain"
                />
            </div>

            {/* Car */}
            <img
                src={`/cars/${teamId}.png`}
                alt={teamName}
                className="absolute bottom-2 md:bottom-4 left-1/2 -translate-x-1/2 w-[60%] md:w-[70%] xl:w-[75%] object-contain pointer-events-none"
            />

            {/* Content */}
            <div className="relative z-10 h-full flex flex-col p-4 md:p-6 pb-24 md:pb-32">

                <div
                    className="text-white/80 text-[16px] md:text-[20px]"
                    style={{
                        fontFamily: 'KHInterferenceF1',
                    }}
                >
                    P{position}
                </div>

                <div className="mt-2">
                    <h3
                        className="text-white leading-none text-[24px] md:text-[36px] "
                        style={{
                            fontFamily: 'Formula1B',
                        }}
                    >
                        {teamName}
                    </h3>
                </div>

                <div className="mt-0 flex gap-5 md:gap-8">

                    <div>
                        <div
                            className="text-white text-[18px] md:text-[22px]"
                            style={{
                                fontFamily: 'KHInterferenceF1',
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
                            className="text-white text-[18px] md:text-[22px]"
                            style={{
                                fontFamily: 'KHInterferenceF1',
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