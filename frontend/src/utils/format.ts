// Date helpers
export function formatDate(dateStr: string, opts?: Intl.DateTimeFormatOptions): string {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric', ...opts,
    });
}

export function formatDateShort(dateStr: string): string {
    return formatDate(dateStr, { day: '2-digit', month: 'short' });
}

export function isPast(dateStr: string): boolean {
    return new Date(dateStr) < new Date();
}

// Number helpers
export function formatProbability(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
}

export function ordinal(n: number): string {
    const s = ['th', 'st', 'nd', 'rd'];
    const v = n % 100;
    return n + (s[(v - 20) % 10] ?? s[v] ?? s[0]);
}

// Race name — strip "Grand Prix" for compact display
export function formatRaceName(name: string, compact = false): string {
    if (!compact) return name;
    return name.replace(' Grand Prix', ' GP');
}

// Country flag emoji via Unicode region indicator
export function countryFlag(countryName: string): string {
    const map: Record<string, string> = {
        bahrain: '🇧🇭', saudi: '🇸🇦', australia: '🇦🇺', japan: '🇯🇵',
        china: '🇨🇳', miami: '🇺🇸', usa: '🇺🇸', 'united states': '🇺🇸',
        emilia: '🇮🇹', italy: '🇮🇹', monaco: '🇲🇨', canada: '🇨🇦',
        spain: '🇪🇸', austria: '🇦🇹', uk: '🇬🇧', 'great britain': '🇬🇧',
        hungary: '🇭🇺', belgium: '🇧🇪', netherlands: '🇳🇱', singapore: '🇸🇬',
        mexico: '🇲🇽', brazil: '🇧🇷', 'las vegas': '🇺🇸', qatar: '🇶🇦',
        'abu dhabi': '🇦🇪', uae: '🇦🇪', azerbaijan: '🇦🇿',
    };
    const key = countryName.toLowerCase();
    for (const [k, flag] of Object.entries(map)) {
        if (key.includes(k)) return flag;
    }
    return '🏁';
}