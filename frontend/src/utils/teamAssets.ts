export const TEAM_LOGOS: Record<string, string> = {
    mercedes: "/team_logo/mercedeslogo.png",
    ferrari: "/team_logo/ferrarilogo.png",
    mclaren: "/team_logo/mclarenlogo.png",
    red_bull: "/team_logo/redbullracinglogo.png",
    aston_martin: "/team_logo/astonmartinlogo.png",
    alpine: "/team_logo/alpinelogo.png",
    haas: "/team_logo/haasf1teamlogo.png",
    rb: "/team_logo/racingbullslogo.png",
    williams: "/team_logo/williamslogo.png",
    audi: "/team_logo/audilogo.png",
    cadillac: "/team_logo/cadillaclogo.png",
};

export function getTeamLogo(teamId: string): string {
    return TEAM_LOGOS[teamId] ?? "/team_logo/defaultlogo.png";
}