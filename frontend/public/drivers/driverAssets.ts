// Driver headshot images live in public/drivers/<CODE>.png
// Naming: exact 3-letter Ergast driver code, uppercase (VER.png, NOR.png …)
// Add DEFAULT.png as fallback for unknown drivers

export function getDriverHeadshot(driverCode: string): string {
    return `/drivers/${driverCode.toUpperCase()}.png`;
}

// Full names mapped to Ergast 3-letter codes
export const DRIVER_NAMES: Record<string, string> = {
    VER: 'Max Verstappen',
    NOR: 'Lando Norris',
    LEC: 'Charles Leclerc',
    HAM: 'Lewis Hamilton',
    RUS: 'George Russell',
    PIA: 'Oscar Piastri',
    SAI: 'Carlos Sainz',
    ALO: 'Fernando Alonso',
    STR: 'Lance Stroll',
    TSU: 'Yuki Tsunoda',
    HUL: 'Nico Hülkenberg',
    ALB: 'Alexander Albon',
    GAS: 'Pierre Gasly',
    OCO: 'Esteban Ocon',
    BOT: 'Valtteri Bottas',
    MAG: 'Kevin Magnussen',
    LAW: 'Liam Lawson',
    BEA: 'Oliver Bearman',
    ANT: 'Kimi Antonelli',
    DOO: 'Jack Doohan',
    HAD: 'Isack Hadjar',
    COL: 'Franco Colapinto',
    SAR: 'Logan Sargeant',
    RIC: 'Daniel Ricciardo',
    ZHO: 'Guanyu Zhou',
    PER: 'Sergio Pérez',
    DEV: 'Nyck de Vries',
    MSC: 'Mick Schumacher',
};

export function getDriverFullName(driverCode: string): string {
    return DRIVER_NAMES[driverCode.toUpperCase()] ?? driverCode;
}

// Split full name into first + last for display
export function splitDriverName(driverCode: string): { first: string; last: string } {
    const full = getDriverFullName(driverCode);
    const parts = full.split(' ');
    if (parts.length < 2) return { first: '', last: full };
    const first = parts[0];
    const last = parts.slice(1).join(' ');
    return { first, last };
}