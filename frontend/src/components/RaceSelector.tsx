import { useRef, useEffect } from 'react';
import type { RaceListItem } from '../types/api';
import { formatDateShort, countryFlag, isPast } from '../utils/format';

interface RaceSelectorProps {
    races: RaceListItem[];
    selectedKey: string | null;
    onSelect: (key: string) => void;
}

export function RaceSelector({ races, selectedKey, onSelect }: RaceSelectorProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const selectedRef = useRef<HTMLButtonElement>(null);

    // Scroll selected item into view on mount / change
    useEffect(() => {
        if (selectedRef.current && containerRef.current) {
            selectedRef.current.scrollIntoView({
                behavior: 'smooth',
                inline: 'center',
                block: 'nearest',
            });
        }
    }, [selectedKey]);

    return (
        <div
            ref={containerRef}
            className="flex gap-2 overflow-x-auto scrollbar-hide py-2 px-4"
        >
            {races.map((race) => {
                const isSelected = race.race_key === selectedKey;
                const past = isPast(race.race_date);

                return (
                    <button
                        key={race.race_key}
                        ref={isSelected ? selectedRef : undefined}
                        onClick={() => onSelect(race.race_key)}
                        disabled={!race.has_predictions}
                        className={`
              shrink-0 flex flex-col items-center gap-1 px-3 py-2 rounded-sm
              border transition-all duration-200 text-left
              ${isSelected
                                ? 'border-[var(--accent-red)] bg-[var(--accent-red)]/10'
                                : 'border-[var(--border-default)] bg-[var(--bg-surface)] hover:border-[var(--text-muted)]'}
              ${!race.has_predictions ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
            `}
                    >
                        {/* Flag + round */}
                        <div className="flex items-center gap-1.5">
                            <span className="text-sm leading-none">
                                {countryFlag(race.country ?? race.race_name)}
                            </span>
                            <span
                                className={`font-mono text-[10px] ${isSelected ? 'text-[var(--accent-red)]' : 'text-[var(--text-muted)]'
                                    }`}
                            >
                                R{race.round}
                            </span>
                        </div>

                        {/* Race label */}
                        <span
                            className={`font-display font-semibold text-xs whitespace-nowrap ${isSelected ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'
                                }`}
                        >
                            {race.country ?? race.race_name.replace(' Grand Prix', '')}
                        </span>

                        {/* Date */}
                        <span className="font-mono text-[9px] text-[var(--text-muted)]">
                            {formatDateShort(race.race_date)}
                        </span>

                        {/* Completed dot */}
                        {race.is_completed && (
                            <div className="w-1 h-1 rounded-full bg-[var(--text-muted)]" />
                        )}
                        {!past && !race.is_completed && (
                            <div className="w-1 h-1 rounded-full bg-[var(--accent-red)] animate-pulse-dot" />
                        )}
                    </button>
                );
            })}
        </div>
    );
}