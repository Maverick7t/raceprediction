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
            className="
                relative
                overflow-hidden
                rounded-2xl
                h-[320px]
            "
            style={{
                background: theme.primary,
            }}
        >
            {/* Dots */}
            <div
                className="
                    absolute
                    inset-0
                    opacity-20
                "
                style={{
                    backgroundImage:
                        'radial-gradient(circle, rgba(255,255,255,.8) 1px, transparent 1px)',
                    backgroundSize: '6px 6px',
                }}
            />

            {/* Logo */}
            <div
                className="
                    absolute
                    top-6
                    right-6
                    h-14
                    w-14
                    rounded-full
                    bg-black/50
                    flex
                    items-center
                    justify-center
                    backdrop-blur-sm
                "
            >
                <img
                    src={getTeamLogo(teamId)}
                    alt={teamName}
                    className="h-8 w-8 object-contain"
                />
            </div>

            {/* Car */}
            <img
                src={`/cars/${teamId}.png`}
                alt={teamName}
                className="
                    absolute
                    bottom-5
                    left-28
                    w-[75%]
                    object-contain
                    pointer-events-none
                "
            />

            {/* Content */}
            <div className="relative z-10 h-full flex flex-col p-6">

                <div
                    className="text-white/80"
                    style={{
                        fontFamily: 'KHInterferenceF1',
                        fontSize: '20px',
                    }}
                >
                    P{position}
                </div>

                <div className="mt-2">
                    <h3
                        className="text-white"
                        style={{
                            fontFamily: 'Formula1B',
                            fontSize: '36px',
                        }}
                    >
                        {teamName}
                    </h3>
                </div>

                <div className="mt-0 flex gap-8">

                    <div>
                        <div
                            className="text-white"
                            style={{
                                fontFamily: 'KHInterferenceF1',
                                fontSize: '22px',
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
                                fontFamily: 'KHInterferenceF1',
                                fontSize: '22px',
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