type PredictionCardProps = {
  position: number;
  driver: string;
  team: string;
  probability: number;
  teamColor?: string;
};

export default function PredictionCard({
  position,
  driver,
  team,
  probability,
  teamColor = "#00DCFF",
}: PredictionCardProps) {
  return (
    <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-slate-800/60 to-slate-900/80 border border-slate-700/50 p-4 hover:border-cyan-500/50 transition-colors group">
      {/* Position Badge */}
      <div className="absolute top-3 right-3 bg-cyan-500/20 border border-cyan-500/50 rounded-lg px-2.5 py-1 text-xs font-bold text-cyan-300 font-mono">
        P{position}
      </div>

      {/* Driver Avatar Placeholder */}
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center mb-3 border border-slate-600/50 group-hover:border-cyan-500/50 transition-colors">
        <span className="text-sm font-bold text-slate-200 font-mono">
          {driver
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </span>
      </div>

      {/* Driver */}
      <h3 className="text-lg font-bold text-white font-barlow mb-1 truncate">
        {driver}
      </h3>

      <p className="text-xs text-slate-400 font-mono mb-4 truncate">
        {team}
      </p>

      {/* Probability */}
      <div className="space-y-3">
        <div className="flex items-end justify-between">
          <span className="text-xs text-slate-400 font-mono uppercase tracking-wider">
            Win Probability
          </span>

          <div className="text-2xl font-bold text-cyan-400 font-barlow">
            {probability}%
          </div>
        </div>

        <div
          className="h-1.5 rounded-full bg-slate-700/50 overflow-hidden"
          style={{ "--bar-width": `${probability}%` } as React.CSSProperties}
        >
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full animate-fill-bar"
            style={{ width: `${probability}%` }}
          />
        </div>
      </div>
    </div>
  );
}
