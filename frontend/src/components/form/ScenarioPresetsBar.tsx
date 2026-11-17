import React from 'react';
import { Sparkles, Bolt, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

export interface ScenarioItem {
  key: string;
  title: string;
  description?: string;
  parameters: Record<string, any>;
}

interface ScenarioPresetsBarProps {
  scenarios: Record<string, ScenarioItem>;
  activePreset: string | null;
  onSelectPreset: (scenario: ScenarioItem) => void;
  onFillBaseline: () => void;
  onReset: () => void;
}

export function ScenarioPresetsBar({
  scenarios,
  activePreset,
  onSelectPreset,
  onFillBaseline,
  onReset,
}: ScenarioPresetsBarProps) {
  const scenarioList = Object.entries(scenarios).map(([key, item]) => ({
    ...item,
    key,
  }));

  return (
    <div className="bg-white border border-emerald-200/80 rounded-2xl p-5 sm:p-6 mb-8 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 mb-4 border-b border-emerald-50">
        <div>
          <div className="flex items-center gap-2 text-agri-800 font-extrabold text-base">
            <Sparkles className="w-5 h-5 text-agri-600" />
            <span>Quick Farm Scenario Presets</span>
          </div>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Select a verified regional scenario to pre-fill all 22 agronomic parameters instantly, or use the quick-fill baseline.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            leftIcon={<Bolt className="w-3.5 h-3.5" />}
            onClick={onFillBaseline}
          >
            Auto-Fill Baseline
          </Button>

          <Button
            type="button"
            variant="outline"
            size="sm"
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
            onClick={onReset}
          >
            Reset
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2.5 items-center">
        {scenarioList.map((sc) => {
          const isActive = activePreset === sc.key;
          const isAlert = sc.key.includes('alert') || sc.key.includes('stress');

          return (
            <button
              key={sc.key}
              type="button"
              onClick={() => onSelectPreset(sc)}
              className={cn(
                'inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-bold border transition-all duration-200 cursor-pointer select-none',
                isActive
                  ? isAlert
                    ? 'bg-red-600 text-white border-red-600 shadow-md shadow-red-600/25'
                    : 'bg-agri-800 text-white border-agri-800 shadow-md shadow-agri-800/25'
                  : isAlert
                  ? 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100 hover:border-red-300'
                  : 'bg-slate-50 text-slate-700 border-slate-200/90 hover:bg-emerald-50 hover:text-agri-800 hover:border-emerald-300'
              )}
            >
              <span>{sc.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
