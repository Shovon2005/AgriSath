import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200/90 rounded-2xl p-6 sm:p-8 shadow-card transition-all duration-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export interface CardHeaderProps {
  icon?: React.ReactNode;
  iconBgClass?: string;
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  className?: string;
}

export function CardHeader({
  icon,
  iconBgClass = 'bg-agri-100 text-agri-800',
  title,
  subtitle,
  badge,
  className,
}: CardHeaderProps) {
  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-4 pb-5 mb-6 border-b border-slate-100',
        className
      )}
    >
      <div className="flex items-center gap-3.5">
        {icon && (
          <div
            className={cn(
              'w-11 h-11 rounded-xl flex items-center justify-center text-xl shrink-0 shadow-sm',
              iconBgClass
            )}
          >
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-lg font-extrabold text-slate-900 tracking-tight m-0">
            {title}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-500 font-medium m-0 mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {badge && <div className="shrink-0">{badge}</div>}
    </div>
  );
}
