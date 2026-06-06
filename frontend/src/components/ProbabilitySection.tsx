import type React from "react";
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
                    const probability = Math.round(
                        (driver.predicted_winner_prob || 0) * 100
                    );

                    return (
                        <div
                            key={driver.driver_code}
                            className="flex items-center gap-4 p-3 rounded-lg bg-slate-800/40"
                        >
                            <div className="flex-1 ">
                                <div className="flex items-baseline gap-2">
                                    <h3 className="font-f1 text-white tracking-[0.03em]">
                                        <span className="sm:hidden">
                                            {driver.driver_code}
                                        </span>

                                        <span className="hidden sm:inline">
                                            {driver.driver_name || driver.driver_code}
                                        </span>
                                    </h3>

                                    <span className="text-[10px] text-slate-500 font-mono uppercase shrink-0 truncate">
                                        {theme.name.slice(0, 3)}
                                    </span>
                                </div>
                            </div>

                            <div className="w-[35%] min-w-[120px] max-w-[300px]">
                                <div className="h-2 rounded-full bg-slate-700/50 overflow-hidden">
                                    <div
                                        className="h-full rounded-full bg-red-500 animate-fill-bar"
                                        style={{ width: `${probability}%` }}
                                    />
                                </div>
                            </div>

                            <div className="text-right w-16 shrink-0">
                                <span className="font-f1 text-white tracking-[0.03em]">
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