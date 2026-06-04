import { ProbabilityBar } from "./ProbabilityBar";
import { getTeamTheme } from "../utils/teamColors";
import type { RacePrediction } from "../types/api";

type Props = {
    predictions: RacePrediction[];
};

export default function ProbabilitySection({
    predictions,
}: Props) {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="font-apax-th-superbold text-white text-3xl tracking-[0.03em] uppercase">
                    Winning Probability
                </h2>

                <p className="text-slate-400 text-sm font-mono mt-1">
                    Based on Qualifying
                </p>
            </div>

            <div className="space-y-4">
                {predictions.slice(0, 10).map((driver) => {
                    const theme = getTeamTheme(driver.team_id || "");
                    const probability = Math.round((driver.predicted_winner_prob || 0) * 100);

                    return (
                        <div
                            key={driver.driver_code}
                            className="flex items-center gap-4 p-3 rounded-lg bg-slate-800/40 border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                        >
                            <div className="flex-1 min-w-0">
                                <div className="flex items-baseline gap-2">
                                    <h3 className="font-f1 text-white truncate tracking-[0.03em]">
                                        {driver.driver_name || driver.driver_code}
                                    </h3>

                                    <span className="text-xs text-slate-400 font-mono shrink-0">
                                        {theme.name}
                                    </span>
                                </div>
                            </div>

                            <div className="w-[35%] min-w-[180px] max-w-[500px]">
                                <div
                                    className="h-2 rounded-full bg-slate-700/50 overflow-hidden"
                                    style={{ "--bar-width": `${probability}%` } as React.CSSProperties}
                                >
                                    <div
                                        className="h-full bg-gradient-to-r from-cyan-500 to-cyan-300 rounded-full animate-fill-bar"
                                        style={{ width: `${probability}%` }}
                                    />
                                </div>
                            </div>

                            <div className="text-right w-16 shrink-0">
                                <span className="text-lg font-bold text-cyan-400 font-barlow">
                                    {probability}%
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
