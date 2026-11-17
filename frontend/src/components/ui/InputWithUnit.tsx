import React from 'react';
import { cn } from '@/lib/utils';

export interface InputWithUnitProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  unit?: string;
  error?: string;
  requiredStar?: boolean;
  optionalTag?: boolean;
  helperText?: string;
}

export const InputWithUnit = React.forwardRef<HTMLInputElement, InputWithUnitProps>(
  (
    {
      className,
      label,
      unit,
      error,
      requiredStar,
      optionalTag,
      helperText,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${label.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        <label
          htmlFor={inputId}
          className="text-xs font-bold text-slate-800 flex items-center justify-between"
        >
          <span>
            {label}
            {requiredStar && <span className="text-rose-600 ml-1 font-semibold">*</span>}
          </span>
          {optionalTag && (
            <span className="text-[11px] font-normal text-slate-400">Optional</span>
          )}
        </label>

        <div className="relative flex items-center w-full">
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'w-full h-12 bg-white border rounded-xl text-slate-900 text-sm font-medium transition-all duration-200 outline-none',
              unit ? 'pl-3.5 pr-16' : 'px-3.5',
              error
                ? 'border-rose-500 bg-rose-50/40 focus:ring-4 focus:ring-rose-500/15'
                : 'border-slate-300 hover:border-slate-400 focus:border-agri-600 focus:ring-4 focus:ring-agri-600/15',
              className
            )}
            {...props}
          />
          {unit && (
            <span className="absolute right-2.5 px-2 py-1 bg-slate-100 border border-slate-200 text-slate-600 font-bold text-[11px] rounded-md pointer-events-none select-none">
              {unit}
            </span>
          )}
        </div>

        {error ? (
          <span className="text-xs text-rose-600 font-medium">{error}</span>
        ) : helperText ? (
          <span className="text-xs text-slate-500">{helperText}</span>
        ) : null}
      </div>
    );
  }
);

InputWithUnit.displayName = 'InputWithUnit';
