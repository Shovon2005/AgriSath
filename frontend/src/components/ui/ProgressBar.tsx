import React from 'react';
import { cn } from '@/lib/utils';

export interface ProgressBarProps {
  value: number; // 0 - 100
  max?: number;
  variant?: 'green' | 'amber' | 'red' | 'blue' | 'gradient';
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  variant = 'gradient',
  showLabel = false,
  className,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const fills = {
    green: 'bg-emerald-600',
    amber: 'bg-amber-500',
    red: 'bg-rose-500',
    blue: 'bg-sky-600',
    gradient: 'bg-gradient-to-r from-emerald-500 to-agri-700',
  };

  return (
    <div className={cn('w-full flex items-center gap-2.5', className)}>
      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200/60">
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', fills[variant])}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs font-extrabold text-slate-700 shrink-0 w-11 text-right">
          {percentage.toFixed(1)}%
        </span>
      )}
    </div>
  );
}
