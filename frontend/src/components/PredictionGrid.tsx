import PredictionCard from "./PredictionCard";
import { getTeamTheme } from "../utils/teamColors";
import type { RacePrediction } from "../types/api";

type Props = {
  predictions: RacePrediction[];
};

export default function PredictionGrid({
  predictions,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <h2 className="text-2xl font-bold text-white font-barlow">
          Top Predictions
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {predictions.slice(0, 6).map((driver, index) => {
          const teamTheme = getTeamTheme(driver.team_id || "");
          return (
            <PredictionCard
              key={`${driver.driver_code}-${index}`}
              position={index + 1}
              driver={driver.driver_name || driver.driver_code}
              team={teamTheme.name}
              probability={Math.round((driver.predicted_winner_prob || 0) * 100)}
              teamColor={teamTheme.primary}
            />
          );
        })}
      </div>
    </div>
  );
}
