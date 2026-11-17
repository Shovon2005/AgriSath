'use client';

import React, { useState } from 'react';
import { Sliders, RefreshCw, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { WhatIfResponse } from '@/types/api';
import { api } from '@/lib/api';

interface WhatIfSimulatorProps {
  baselineInputs: Record<string, any>;
  currentCrop: string;
}

export function WhatIfSimulator({ baselineInputs, currentCrop }: WhatIfSimulatorProps) {
  const [testRainfall, setTestRainfall] = useState<number>(baselineInputs.rainfall || 150);
  const [testTemperature, setTestTemperature] = useState<number>(baselineInputs.temperature || 25);
  const [testN, setTestN] = useState<number>(baselineInputs.N || 90);
  const [testSoilType, setTestSoilType] = useState<string>(baselineInputs.soil_type || 'Clay');

  const [isLoading, setIsLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState<WhatIfResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const perturbations: Record<string, any> = {
        rainfall: Number(testRainfall),
        temperature: Number(testTemperature),
        N: Number(testN),
        soil_type: testSoilType,
      };

      const res = await api.simulateWhatIf(baselineInputs, perturbations);
      if (res.status === 'success') {
        setSimulationResult(res);
      } else {
        setError('Simulation failed.');
      }
    } catch (err: any) {
      setError(err.message || 'Simulation error.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-indigo-100">
      <CardHeader
        icon={<Sliders className="w-5 h-5" />}
        iconBgClass="bg-indigo-100 text-indigo-800"
        title="Interactive What-If Simulation Engine"
        subtitle="Perturb climatic and soil parameters to test model sensitivity and crop transitions"
        badge={
          <span className="text-xs font-bold text-indigo-800 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
            Counterfactual XAI
          </span>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Sliders & Controls */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Rainfall: {testRainfall} mm</span>
              <span className="text-slate-400 font-normal">Baseline: {baselineInputs.rainfall} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="500"
              step="5"
              value={testRainfall}
              onChange={(e) => setTestRainfall(Number(e.target.value))}
              className="w-full accent-agri-600 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Temperature: {testTemperature} °C</span>
              <span className="text-slate-400 font-normal">Baseline: {baselineInputs.temperature} °C</span>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              step="0.5"
              value={testTemperature}
              onChange={(e) => setTestTemperature(Number(e.target.value))}
              className="w-full accent-agri-600 cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-700 mb-1">
              <span>Nitrogen (N): {testN} mg/kg</span>
              <span className="text-slate-400 font-normal">Baseline: {baselineInputs.N} mg/kg</span>
            </div>
            <input
              type="range"
              min="0"
              max="200"
              step="5"
              value={testN}
              onChange={(e) => setTestN(Number(e.target.value))}
              className="w-full accent-agri-600 cursor-pointer"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 block mb-1">
              Hypothetical Soil Type
            </label>
            <select
              value={testSoilType}
              onChange={(e) => setTestSoilType(e.target.value)}
              className="w-full h-10 bg-white border border-slate-300 rounded-lg text-xs font-medium px-3 outline-none focus:border-agri-600"
            >
              <option value="Loamy">Loamy</option>
              <option value="Clay">Clay</option>
              <option value="Sandy">Sandy</option>
            </select>
          </div>

          <Button
            type="button"
            variant="primary"
            size="md"
            isLoading={isLoading}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            onClick={handleSimulate}
            className="w-full mt-2"
          >
            Simulate Perturbation
          </Button>

          {error && <span className="text-xs text-rose-600 font-medium block">{error}</span>}
        </div>

        {/* Simulation Output Card */}
        <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200/90 flex flex-col justify-between min-h-[260px]">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-3">
              Counterfactual Simulation Outcome
            </span>

            {simulationResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3.5 rounded-xl bg-white border border-slate-200">
                  <div>
                    <span className="text-xs text-slate-400 font-semibold block">Simulated Crop</span>
                    <span className="text-xl font-black capitalize text-slate-900">
                      {simulationResult.simulated_prediction.crop}
                    </span>
                  </div>
                  <Badge
                    variant={simulationResult.crop_changed ? 'alert' : 'high'}
                  >
                    {simulationResult.crop_changed ? 'Crop Changed' : 'Optimal Stable'}
                  </Badge>
                </div>

                <div className="flex justify-between items-center text-xs text-slate-600 px-1">
                  <span>Confidence Impact:</span>
                  <span className={`font-black text-sm ${simulationResult.confidence_delta >= 0 ? 'text-emerald-700' : 'text-rose-600'}`}>
                    {simulationResult.confidence_delta >= 0 ? `+${simulationResult.confidence_delta.toFixed(1)}%` : `${simulationResult.confidence_delta.toFixed(1)}%`}
                  </span>
                </div>

                {simulationResult.crop_changed && (
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs">
                    💡 Threshold exceeded: Transitioned from <strong>{currentCrop}</strong> to <strong>{simulationResult.simulated_prediction.crop}</strong> due to perturbed soil/climatic thresholds.
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center text-slate-400">
                <Sliders className="w-10 h-10 mb-2 stroke-[1.5]" />
                <p className="text-xs">Adjust sliders and click &ldquo;Simulate Perturbation&rdquo; to test model reaction.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
