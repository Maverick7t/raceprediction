import { useEffect, useRef, useState } from 'react';
import { formatProbability } from '../utils/format';

interface ProbabilityBarProps {
    value: number;         // 0–1
    color: string;         // CSS hex / var
    label?: string;
    showLabel?: boolean;
    height?: number;       // px
    className?: string;
}

export function ProbabilityBar({
    value,
    color,
    label,
    showLabel = true,
    height = 4,
    className = '',
}: ProbabilityBarProps) {
    const [width, setWidth] = useState(0);
    const mounted = useRef(false);

    useEffect(() => {
        // Defer to let the row animation settle first
        const t = setTimeout(() => {
            mounted.current = true;
            setWidth(Math.min(Math.max(value, 0), 1) * 100);
        }, 80);
        return () => clearTimeout(t);
    }, [value]);

    return (
        <div className={`flex items-center gap-2 ${className}`}>
            {/* Track */}
            <div
                className="relative flex-1 rounded-full overflow-hidden"
                style={{ height, background: 'var(--bg-elevated)' }}
            >
                {/* Fill */}
                <div
                    className="absolute left-0 top-0 h-full rounded-full"
                    style={{
                        width: `${width}%`,
                        background: color,
                        transition: 'width 0.7s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                />
            </div>
            {showLabel && (
                <span className="font-mono text-[11px] text-[var(--text-secondary)] w-10 text-right shrink-0">
                    {label ?? formatProbability(value)}
                </span>
            )}
        </div>
    );
}