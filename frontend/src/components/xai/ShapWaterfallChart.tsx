'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import { Brain, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { FeatureImportanceItem, ShapWaterfall } from '@/types/api';

interface ShapWaterfallChartProps {
  cropName: string;
  importantFeatures?: FeatureImportanceItem[];
  waterfall?: ShapWaterfall;
}

export function ShapWaterfallChart({
  cropName,
  importantFeatures = [],
  waterfall,
}: ShapWaterfallChartProps) {
  // Use waterfall driving factors if available, or fall back to important_features
  const chartData = (waterfall?.driving_factors || []).length > 0
    ? waterfall!.driving_factors.map((f) => ({
        name: f.feature,
        value: parseFloat(Number(f.contribution).toFixed(3)),
        direction: f.direction,
        raw: `${f.value}`,
      }))
    : importantFeatures.map((f) => ({
        name: f.feature,
        value: parseFloat(Number(f.importance).toFixed(3)),
        direction: f.direction || (f.importance >= 0 ? 'positive' : 'negative'),
        raw: '',
      }));

  if (chartData.length === 0) return null;

  return (
    <Card className="border-emerald-100">
      <CardHeader
        icon={<Brain className="w-5 h-5" />}
        iconBgClass="bg-emerald-100 text-emerald-800"
        title="Explainable AI (TreeExplainer SHAP)"
        subtitle={`Exact localized feature contributions determining recommendation for ${cropName}`}
        badge={
          <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
            Local Instance XAI
          </span>
        }
      />

      <div className="flex flex-col lg:flex-row gap-6 items-center">
        {/* Recharts Bar Chart */}
        <div className="w-full lg:w-3/5 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
            >
              <XAxis type="number" domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fontWeight: 600 }} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="bg-slate-900 text-white p-2.5 rounded-lg text-xs shadow-lg">
                        <strong className="block mb-1">{d.name}</strong>
                        <div>Contribution: <span className="font-bold">{d.value > 0 ? `+${d.value}` : d.value}</span></div>
                        {d.raw && <div>Input Value: <span className="text-emerald-300 font-bold">{d.raw}</span></div>}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <ReferenceLine x={0} stroke="#94a3b8" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.direction === 'positive' || entry.value >= 0 ? '#16a34a' : '#ef4444'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Narrative Breakdown */}
        <div className="w-full lg:w-2/5 flex flex-col gap-2.5">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Directional Driver Insights
          </span>
          <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
            {chartData.map((item, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2">
                  {item.value >= 0 ? (
                    <ArrowUpRight className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-rose-600 shrink-0" />
                  )}
                  <div>
                    <span className="font-bold text-slate-800 block">{item.name}</span>
                    {item.raw && <span className="text-[11px] text-slate-500">Value: {item.raw}</span>}
                  </div>
                </div>
                <span
                  className={`font-black text-xs px-2 py-0.5 rounded-md ${
                    item.value >= 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                  }`}
                >
                  {item.value > 0 ? `+${item.value}` : item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
