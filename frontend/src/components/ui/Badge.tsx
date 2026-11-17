import React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'high' | 'medium' | 'low' | 'info' | 'alert' | 'neutral';
  dot?: boolean;
}

export function Badge({
  className,
  variant = 'neutral',
  dot = false,
  children,
  ...props
}: BadgeProps) {
  const variants = {
    high: 'bg-emerald-50 text-emerald-800 border-emerald-200/80',
    medium: 'bg-amber-50 text-amber-800 border-amber-200/80',
    low: 'bg-rose-50 text-rose-800 border-rose-200/80',
    info: 'bg-sky-50 text-sky-800 border-sky-200/80',
    alert: 'bg-red-50 text-red-800 border-red-300 font-bold',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const dots = {
    high: 'bg-emerald-500',
    medium: 'bg-amber-500',
    low: 'bg-rose-500',
    info: 'bg-sky-500',
    alert: 'bg-red-600 animate-pulse',
    neutral: 'bg-slate-400',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border select-none whitespace-nowrap',
        variants[variant],
        className
      )}
      {...props}
    >
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dots[variant])} />}
      {children}
    </span>
  );
}
