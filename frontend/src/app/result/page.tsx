'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Sprout,
  FileDown,
  ArrowLeft,
  Mountain,
  Droplets,
  FlaskConical,
  AlertTriangle,
  Award,
  Layers,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Button } from '@/components/ui/Button';
import { PredictResponse } from '@/types/api';
import { api } from '@/lib/api';
import { ShapWaterfallChart } from '@/components/xai/ShapWaterfallChart';
import { WhatIfSimulator } from '@/components/xai/WhatIfSimulator';

export default function ResultPage() {
  const [data, setData] = useState<PredictResponse | null>(null);
  const [inputs, setInputs] = useState<Record<string, any>>({});
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('agrisathi_latest_prediction');
      const storedInputs = sessionStorage.getItem('agrisathi_latest_inputs');
      if (stored) {
        setData(JSON.parse(stored));
      }
      if (storedInputs) {
        setInputs(JSON.parse(storedInputs));
      }
    } catch (e) {
      console.error('Error parsing stored prediction:', e);
    }
  }, []);

  const handleDownloadPdf = async () => {
    setIsDownloadingPdf(true);
    try {
      await api.downloadReportPdf(inputs, `agrisathi_advisory_${data?.prediction?.recommended_crop || 'crop'}.pdf`);
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  if (!data || !data.prediction) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-4">
          <Sprout className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-800 mb-2">No Active Advisory Session</h2>
        <p className="text-sm text-slate-500 max-w-md mb-6">
          Submit farm parameters on the homepage or choose a regional scenario preset to generate an intelligent advisory report.
        </p>
        <Link href="/">
          <Button variant="primary" leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Back to Form
          </Button>
        </Link>
      </div>
    );
  }

  const { prediction, advisory } = data;
  const soil = advisory?.soil;
  const irrigation = advisory?.irrigation;
  const fertilizer = advisory?.fertilizer;
  const hazards = advisory?.hazards || advisory?.risks;

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Top Action Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link href="/">
          <Button variant="outline" size="sm" leftIcon={<ArrowLeft className="w-4 h-4" />}>
            New Assessment
          </Button>
        </Link>

        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="md"
            isLoading={isDownloadingPdf}
            leftIcon={<FileDown className="w-4 h-4" />}
            onClick={handleDownloadPdf}
          >
            Download Official Agronomic PDF
          </Button>
        </div>
      </div>

      {/* Hero Recommendation Card */}
      <div className="bg-gradient-to-br from-agri-900 via-agri-800 to-emerald-900 text-white rounded-3xl p-6 sm:p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-400/30 mb-3">
              <Award className="w-3.5 h-3.5" />
              <span>Optimal Agronomic Crop Match</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-black capitalize tracking-tight leading-tight mb-2">
              {prediction.recommended_crop}
            </h1>
            <p className="text-emerald-200/90 text-xs sm:text-sm max-w-xl font-medium">
              Ranked highest based on random forest classification and SHAP feature alignment across soil chemistry, temperature, moisture, and local agro-climate.
            </p>
          </div>

          <div className="flex flex-col items-start md:items-end gap-2 shrink-0 bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/10">
            <span className="text-xs font-bold text-emerald-200 uppercase tracking-wider">
              AI Confidence Score
            </span>
            <span className="text-4xl sm:text-5xl font-black text-white">
              {prediction.confidence.toFixed(1)}%
            </span>
            <div className="w-36 mt-1">
              <ProgressBar value={prediction.confidence} variant="green" />
            </div>
          </div>
        </div>
      </div>

      {/* Top-3 Crop Suitability Comparison Matrix */}
      {prediction.top_3_crops && prediction.top_3_crops.length > 0 && (
        <Card className="border-slate-200">
          <CardHeader
            icon={<Layers className="w-5 h-5" />}
            iconBgClass="bg-emerald-100 text-emerald-800"
            title="Top-3 Crop Recommendations Comparison"
            subtitle="Multi-attribute suitability ranking against farm agro-climatic envelopes"
          />

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-extrabold text-[11px] tracking-wider">
                  <th className="py-3.5 px-4">Rank</th>
                  <th className="py-3.5 px-4">Crop Candidate</th>
                  <th className="py-3.5 px-4">AI Confidence</th>
                  <th className="py-3.5 px-4">Suitability Score</th>
                  <th className="py-3.5 px-4">Water Requirement</th>
                  <th className="py-3.5 px-4">Season Alignment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
                {prediction.top_3_crops.map((c, i) => (
                  <tr key={c.crop} className={i === 0 ? 'bg-emerald-50/40' : 'hover:bg-slate-50/60'}>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs ${i === 0 ? 'bg-agri-700 text-white' : 'bg-slate-200 text-slate-700'}`}>
                        #{c.rank || i + 1}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900 capitalize flex items-center gap-2">
                      <Sprout className="w-4 h-4 text-emerald-600" />
                      <span>{c.crop}</span>
                    </td>
                    <td className="py-3.5 px-4 font-extrabold text-agri-800">
                      {c.confidence.toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {c.suitability_score ? `${c.suitability_score}/100` : '-'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {c.water_match || 'Medium'}
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant="high">Aligned</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 4 Core Advisory Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Module 1: Soil Fertility */}
        {soil && (
          <Card className="border-emerald-100 flex flex-col justify-between">
            <div>
              <CardHeader
                icon={<Mountain className="w-5 h-5" />}
                iconBgClass="bg-emerald-100 text-emerald-800"
                title="Module 1: Soil Health & Fertility"
                subtitle="Soil reaction, salinity hazard, and macro-nutrient balance"
                badge={
                  <Badge variant={soil.fertility_class === 'High' ? 'high' : soil.fertility_class === 'Medium' ? 'medium' : 'low'} dot>
                    {soil.fertility_class} Fertility ({soil.soil_score}/100)
                  </Badge>
                }
              />
              <div className="space-y-3 text-xs sm:text-sm text-slate-700">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex justify-between items-center">
                  <span className="font-semibold text-slate-600">Soil Reaction &amp; pH:</span>
                  <span className="font-bold text-slate-900">{soil.ph_status}</span>
                </div>
                {soil.ph_recommendation && (
                  <p className="text-xs text-slate-500 italic pl-1">{soil.ph_recommendation}</p>
                )}

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex justify-between items-center">
                  <span className="font-semibold text-slate-600">Salinity Hazard (EC):</span>
                  <span className="font-bold text-slate-900">{soil.salinity_hazard}</span>
                </div>

                {soil.improvement_actions && soil.improvement_actions.length > 0 && (
                  <div className="pt-2">
                    <span className="text-xs font-bold text-slate-700 block mb-1.5 uppercase tracking-wider">Corrective Action Plan:</span>
                    <ul className="list-disc list-inside space-y-1 text-xs text-slate-600">
                      {soil.improvement_actions.map((act, i) => (
                        <li key={i}>{act}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </Card>
        )}

        {/* Module 3: Smart Irrigation */}
        {irrigation && (
          <Card className="border-sky-100 flex flex-col justify-between">
            <div>
              <CardHeader
                icon={<Droplets className="w-5 h-5" />}
                iconBgClass="bg-sky-100 text-sky-800"
                title="Module 3: Smart Irrigation Advisory"
                subtitle="Evapotranspiration (ETc) volume and scheduled irrigation timing"
                badge={
                  <Badge variant={irrigation.priority === 'High' ? 'low' : irrigation.priority === 'Medium' ? 'medium' : 'high'} dot>
                    {irrigation.priority} Priority
                  </Badge>
                }
              />
              <div className="space-y-3 text-xs sm:text-sm text-slate-700">
                <div className="p-3.5 rounded-xl bg-sky-50/60 border border-sky-100 flex justify-between items-center">
                  <span className="font-semibold text-sky-900">Total Farm Water Needed:</span>
                  <span className="text-lg font-black text-sky-950">
                    {irrigation.total_farm_litres?.toLocaleString()} Litres
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex justify-between items-center">
                  <span className="font-semibold text-slate-600">Crop Daily Water (ETc):</span>
                  <span className="font-bold text-slate-900">{irrigation.daily_water_requirement_mm} mm/day</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex justify-between items-center">
                  <span className="font-semibold text-slate-600">Irrigation Timing Window:</span>
                  <span className="font-bold text-slate-900">{irrigation.next_irrigation_time}</span>
                </div>

                {irrigation.recommendations && irrigation.recommendations.length > 0 && (
                  <div className="pt-2">
                    <span className="text-xs font-bold text-slate-700 block mb-1 uppercase tracking-wider">Water Guidelines:</span>
                    <p className="text-xs text-slate-600 m-0">{irrigation.recommendations[0]}</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        )}

        {/* Module 4: Fertilizer Dosing */}
        {fertilizer && (
          <Card className="border-emerald-100 flex flex-col justify-between">
            <div>
              <CardHeader
                icon={<FlaskConical className="w-5 h-5" />}
                iconBgClass="bg-emerald-100 text-emerald-800"
                title="Module 4: Commercial Fertilizer Plan"
                subtitle="Calculated NPK deficits and commercial fertilizer split doses"
              />
              {fertilizer.commercial_fertilizers && (
                <div className="space-y-3 text-xs sm:text-sm">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200/70">
                      <span className="text-xs font-bold text-emerald-700 block">Urea (46% N)</span>
                      <span className="text-base font-black text-emerald-950">{fertilizer.commercial_fertilizers.urea_kg_ha} kg/ha</span>
                    </div>
                    <div className="p-3 rounded-xl bg-amber-50 border border-amber-200/70">
                      <span className="text-xs font-bold text-amber-700 block">DAP (18-46-0)</span>
                      <span className="text-base font-black text-amber-950">{fertilizer.commercial_fertilizers.dap_kg_ha} kg/ha</span>
                    </div>
                    <div className="p-3 rounded-xl bg-rose-50 border border-rose-200/70">
                      <span className="text-xs font-bold text-rose-700 block">MOP (60% K)</span>
                      <span className="text-base font-black text-rose-950">{fertilizer.commercial_fertilizers.mop_kg_ha} kg/ha</span>
                    </div>
                  </div>

                  {fertilizer.organic_alternatives && fertilizer.organic_alternatives.length > 0 && (
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-xs font-bold text-slate-700 block mb-1">Organic Soil Amendments:</span>
                      <p className="text-xs text-slate-600 m-0">{fertilizer.organic_alternatives.join(' • ')}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Module 5: Hazard Risks Matrix */}
        {hazards && (
          <Card className="border-amber-100 flex flex-col justify-between">
            <div>
              <CardHeader
                icon={<AlertTriangle className="w-5 h-5" />}
                iconBgClass="bg-amber-100 text-amber-800"
                title="Module 5: Environmental Risk Diagnostics"
                subtitle="Frost, pest pressure, heat stress, and fungal foliar hazards"
                badge={
                  <Badge variant={hazards.overall_risk_level === 'High' ? 'alert' : hazards.overall_risk_level === 'Medium' ? 'medium' : 'high'} dot>
                    {hazards.overall_risk_level || 'Low'} Risk Level
                  </Badge>
                }
              />
              <div className="space-y-2.5 text-xs sm:text-sm">
                {hazards.active_hazards && hazards.active_hazards.length > 0 ? (
                  hazards.active_hazards.map((hz, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-amber-50/50 border border-amber-200/80">
                      <div className="flex justify-between items-center mb-1">
                        <strong className="text-amber-900">{hz.hazard}</strong>
                        <Badge variant={hz.severity === 'High' ? 'alert' : 'medium'}>{hz.severity}</Badge>
                      </div>
                      <p className="text-xs text-slate-600 mb-1"><strong>Trigger:</strong> {hz.trigger}</p>
                      <p className="text-xs text-emerald-800 font-semibold m-0"><strong>Mitigation:</strong> {hz.mitigation}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
                    ✓ All environmental telemetry within safe agronomic boundaries. No acute hazards detected.
                  </div>
                )}
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Module 6: Explainable AI SHAP Waterfall Chart */}
      <ShapWaterfallChart
        cropName={prediction.recommended_crop}
        importantFeatures={prediction.important_features}
        waterfall={prediction.waterfall}
      />

      {/* Module 7: Interactive What-If Simulation */}
      <WhatIfSimulator
        baselineInputs={inputs}
        currentCrop={prediction.recommended_crop}
      />
    </div>
  );
}
