import React from 'react';
import { Sprout } from 'lucide-react';

export function Footer() {
  return (
    <footer className="w-full bg-slate-900 text-slate-400 py-12 border-t border-slate-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center text-center gap-4">
        <div className="flex items-center gap-2 text-white font-extrabold text-lg">
          <div className="w-8 h-8 rounded-lg bg-agri-600 flex items-center justify-center text-white">
            <Sprout className="w-4 h-4" />
          </div>
          <span>AgriSathi</span>
        </div>
        <p className="max-w-xl text-xs sm:text-sm text-slate-400 font-normal leading-relaxed">
          Explainable AI-Driven Intelligent Decision Support Framework for Precision Agriculture.
          Synthesizing soil chemistry, local telemetry, and farm practices for optimized yields.
        </p>
        <div className="text-xs text-slate-500 pt-3 border-t border-slate-800/80 w-full flex flex-wrap justify-between items-center gap-2">
          <span>&copy; {new Date().getFullYear()} AgriSathi Decision Systems. All rights reserved.</span>
          <span>Powered by TreeExplainer SHAP &amp; Random Forest Classifiers</span>
        </div>
      </div>
    </footer>
  );
}
