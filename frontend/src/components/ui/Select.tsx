import React from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
  requiredStar?: boolean;
  options: { value: string; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, requiredStar, options, id, ...props }, ref) => {
    const selectId = id || `select-${label.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        <label
          htmlFor={selectId}
          className="text-xs font-bold text-slate-800 flex items-center"
        >
          {label}
          {requiredStar && <span className="text-rose-600 ml-1 font-semibold">*</span>}
        </label>

        <div className="relative flex items-center w-full">
          <select
            ref={ref}
            id={selectId}
            className={cn(
              'w-full h-12 bg-white border rounded-xl text-slate-900 text-sm font-medium px-3.5 pr-10 appearance-none cursor-pointer transition-all duration-200 outline-none',
              error
                ? 'border-rose-500 bg-rose-50/40 focus:ring-4 focus:ring-rose-500/15'
                : 'border-slate-300 hover:border-slate-400 focus:border-agri-600 focus:ring-4 focus:ring-agri-600/15',
              className
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3.5 w-4 h-4 text-slate-400 pointer-events-none" />
        </div>

        {error && <span className="text-xs text-rose-600 font-medium">{error}</span>}
      </div>
    );
  }
);

Select.displayName = 'Select';
