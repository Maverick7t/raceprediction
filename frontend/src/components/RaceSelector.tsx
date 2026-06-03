// src/components/RaceSelector.tsx

import { useRef, useEffect } from 'react';
import type { RaceListItem } from '../types/api';

interface RaceSelectorProps {
    races: RaceListItem[];
    selectedKey: string | null;
    onSelect: (key: string) => void;
}

export function RaceSelector({
    races,
    selectedKey,
    onSelect,
}: RaceSelectorProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const selectedRef = useRef<HTMLButtonElement>(null);

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

                return (
                    <button
                        key={race.race_key}
                        ref={isSelected ? selectedRef : undefined}
                        onClick={() => onSelect(race.race_key)}
                        disabled={!race.has_predictions}
                        className={`
                            relative
                            shrink-0
                            w-[180px]
                            xl:w-[210px]
                            flex
                            flex-col
                            items-center
                            gap-1
                            px-3
                            py-3
                            text-left
                            transition-all
                            duration-200
                            border
                            border-transparent
                            
                            ${isSelected
                                ? 'bg-transparent'
                                : 'bg-[var(--bg-surface)] hover:bg-[var(--bg-elevated)]/50'
                            }

                            ${!race.has_predictions
                                ? 'opacity-30 cursor-not-allowed'
                                : 'cursor-pointer'
                            }
                        `}
                    >
                        <span
                            className={`font-mono text-[10px] ${isSelected
                                ? 'text-[#8B0000]'
                                : 'text-[var(--text-muted)]'
                                }`}
                        >
                            {race.year} · R{race.round}
                        </span>

                        <span
                            className={`font-f1 text-xs whitespace-nowrap ${isSelected
                                ? 'text-[var(--text-primary)]'
                                : 'text-[var(--text-secondary)]'
                                }`}
                        >
                            {race.race_name}
                        </span>

                        <span
                            className={`font-f1 text-[9px] ${isSelected
                                ? 'text-[var(--text-secondary)]'
                                : 'text-[var(--text-muted)]'
                                }`}
                        >
                            {race.circuit_id}
                        </span>

                        {/* Active race indicator */}
                        {isSelected && (
                            <div
                                className="absolute bottom-0 left-2 right-2 h-[3px] rounded-full"
                                style={{
                                    background: '#8B0000',
                                }}
                            />
                        )}
                    </button>
                );
            })}
        </div>
    );
}