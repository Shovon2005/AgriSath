import React from 'react';
import { ShieldCheck, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface PredictActionBarProps {
  isLoading: boolean;
}

export function PredictActionBar({ isLoading }: PredictActionBarProps) {
  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 sm:p-7 shadow-card flex flex-wrap items-center justify-between gap-5 my-8">
      <div className="max-w-xl">
        <div className="flex items-center gap-2 text-agri-700 font-extrabold text-sm mb-1">
          <ShieldCheck className="w-4 h-4 text-agri-600 shrink-0" />
          <span>Secure Offline AI Inference &amp; TreeExplainer XAI</span>
        </div>
        <p className="text-xs text-slate-500 font-medium leading-relaxed m-0">
          All 22 farm variables are checked against agronomic boundary envelopes before triggering Random Forest inference and multi-module advisory calculations.
        </p>
      </div>

      <Button
        type="submit"
        size="lg"
        variant="primary"
        isLoading={isLoading}
        leftIcon={<Sparkles className="w-5 h-5" />}
        rightIcon={<ArrowRight className="w-5 h-5" />}
        className="text-base px-8 py-4 shadow-lg shadow-agri-800/30 font-extrabold w-full sm:w-auto"
      >
        Generate AI Advisory
      </Button>
    </div>
  );
}
