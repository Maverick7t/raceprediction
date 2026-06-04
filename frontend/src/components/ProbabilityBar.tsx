import { useEffect, useRef, useState } from 'react';
import { formatProbability } from '../utils/format';

interface ProbabilityBarProps {
    value: number;
    color?: string;
    label?: string;
    showLabel?: boolean;
    height?: number;
    className?: string;
}

export function ProbabilityBar({
    value,
    label,
    showLabel = true,
    height = 4,
    className = '',
}: ProbabilityBarProps) {
    const [width, setWidth] = useState(0);
    const mounted = useRef(false);

    useEffect(() => {
        const t = setTimeout(() => {
            mounted.current = true;
            setWidth(Math.min(Math.max(value, 0), 1) * 100);
        }, 80);

        return () => clearTimeout(t);
    }, [value]);

    return (
        <div className={`flex items-center gap-2 ${className}`}>
            <div
                className="relative flex-1 rounded-full overflow-hidden"
                style={{
                    height,
                    background: 'rgba(71,85,105,0.35)',
                }}
            >
                <div
                    className="absolute left-0 top-0 h-full rounded-full"
                    style={{
                        width: `${width}%`,
                        background: '#ef4444',
                        transition:
                            'width 0.7s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                />
            </div>

            {showLabel && (
                <span className="font-mono text-[16px] text-slate-400 w-10 text-right shrink-0">
                    {label ?? formatProbability(value)}
                </span>
            )}
        </div>
    );
}