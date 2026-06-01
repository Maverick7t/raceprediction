import React from "react";

type HeroRaceCardProps = {
  raceName: string;
  round: number;
  raceDate: string;
  winner: string;
  team: string;
  probability: number;
};

export default function HeroRaceCard({
  raceName,
  round,
  raceDate,
  winner,
  team,
  probability,
}: HeroRaceCardProps) {
  const confidence =
    probability >= 80
      ? "High"
      : probability >= 60
      ? "Medium"
      : "Low";

  return (
    <div className="relative w-full max-w-2xl mx-auto overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8 shadow-2xl">
      {/* Background glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-transparent opacity-50 blur-3xl" />

      {/* Circuit watermark */}
      <div className="absolute top-4 right-6 text-6xl font-bold text-slate-700/30 font-barlow">
        F1
      </div>

      {/* Content */}
      <div className="relative z-10 space-y-6">
        <div className="flex items-center space-x-2">
          <span className="text-cyan-400 text-sm font-semibold font-mono">
            Round {round}
          </span>
        </div>

        <h1 className="text-5xl font-bold text-white font-barlow tracking-tight">
          {raceName}
        </h1>

        <p className="text-slate-400 text-lg font-mono">
          {raceDate}
        </p>

        <div className="bg-gradient-to-r from-cyan-900/40 to-slate-900/40 border border-cyan-500/30 rounded-xl p-6 space-y-4">
          <div className="flex items-baseline space-x-3">
            <span className="text-slate-300 text-sm font-semibold font-mono">
              AI Winner Prediction
            </span>
          </div>

          <div className="flex items-end space-x-6">
            <div className="space-y-1">
              <div className="text-6xl font-bold text-cyan-400 font-barlow">
                {probability}%
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-2xl font-bold text-white font-barlow">
                {winner}
              </p>

              <p className="text-slate-300 font-mono">
                {team}
              </p>
            </div>
          </div>

          <div className="text-sm text-cyan-300 font-mono pt-2">
            Confidence: {confidence}
          </div>
        </div>
      </div>
    </div>
  );
}
