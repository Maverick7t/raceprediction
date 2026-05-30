export interface TeamTheme {
    primary: string;
    secondary: string;
    text: string;
    name: string;
    abbrev: string;
}

const TEAM_THEMES: Record<string, TeamTheme> = {
    // 2024 / 2025 teams
    red_bull: { primary: '#3671C6', secondary: '#CC1E4A', text: '#fff', name: 'Red Bull Racing', abbrev: 'RBR' },
    redbull: { primary: '#3671C6', secondary: '#CC1E4A', text: '#fff', name: 'Red Bull Racing', abbrev: 'RBR' },
    ferrari: { primary: '#E8002D', secondary: '#FFD700', text: '#fff', name: 'Ferrari', abbrev: 'FER' },
    mercedes: { primary: '#00A19C', secondary: '#C0C0C0', text: '#fff', name: 'Mercedes', abbrev: 'MER' },
    mclaren: { primary: '#FF8000', secondary: '#0093CC', text: '#000', name: 'McLaren', abbrev: 'MCL' },
    aston_martin: { primary: '#358C75', secondary: '#6CD3BF', text: '#fff', name: 'Aston Martin', abbrev: 'AMR' },
    astonmartin: { primary: '#358C75', secondary: '#6CD3BF', text: '#fff', name: 'Aston Martin', abbrev: 'AMR' },
    alpine: { primary: '#0093CC', secondary: '#FF87BC', text: '#fff', name: 'Alpine', abbrev: 'ALP' },
    williams: { primary: '#37BEDD', secondary: '#012564', text: '#fff', name: 'Williams', abbrev: 'WIL' },
    racing_bulls: { primary: '#6692FF', secondary: '#C8C8C8', text: '#fff', name: 'Racing Bulls', abbrev: 'RBL' },
    racingbulls: { primary: '#6692FF', secondary: '#C8C8C8', text: '#fff', name: 'Racing Bulls', abbrev: 'RBL' },
    visa_rb: { primary: '#6692FF', secondary: '#C8C8C8', text: '#fff', name: 'Visa RB', abbrev: 'VRB' },
    alphatauri: { primary: '#5E8FAA', secondary: '#FFFFFF', text: '#fff', name: 'AlphaTauri', abbrev: 'AT' },
    haas: { primary: '#B6BABD', secondary: '#E8002D', text: '#000', name: 'Haas', abbrev: 'HAA' },
    haas_f1_team: { primary: '#B6BABD', secondary: '#E8002D', text: '#000', name: 'Haas', abbrev: 'HAA' },
    sauber: { primary: '#00E701', secondary: '#FFFFFF', text: '#000', name: 'Sauber', abbrev: 'SAU' },
    kick_sauber: { primary: '#00E701', secondary: '#FFFFFF', text: '#000', name: 'Kick Sauber', abbrev: 'SAU' },
    alfa_romeo: { primary: '#C92D4B', secondary: '#FFFFFF', text: '#fff', name: 'Alfa Romeo', abbrev: 'ALF' },
};

const FALLBACK: TeamTheme = {
    primary: '#3A3A55',
    secondary: '#6A6A88',
    text: '#fff',
    name: 'Unknown',
    abbrev: '???',
};

export function getTeamTheme(teamId: string): TeamTheme {
    // normalise: lowercase, spaces → underscores
    const key = teamId.toLowerCase().replace(/\s+/g, '_');
    return TEAM_THEMES[key] ?? FALLBACK;
}