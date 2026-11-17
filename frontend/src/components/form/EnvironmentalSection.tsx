import React from 'react';
import { CloudSun, SatelliteDish } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { InputWithUnit } from '@/components/ui/InputWithUnit';
import { FarmInputs } from '@/types/schemas';

interface EnvironmentalSectionProps {
  formData: Partial<FarmInputs>;
  errors: Record<string, string>;
  onChange: (field: keyof FarmInputs, value: any) => void;
}

export function EnvironmentalSection({
  formData,
  errors,
  onChange,
}: EnvironmentalSectionProps) {
  const handleNumericChange = (field: keyof FarmInputs, rawVal: string) => {
    if (rawVal === '') {
      onChange(field, undefined);
      return;
    }
    const num = parseFloat(rawVal);
    onChange(field, isNaN(num) ? rawVal : num);
  };

  return (
    <Card className="border-teal-100">
      <CardHeader
        icon={<CloudSun className="w-5 h-5" />}
        iconBgClass="bg-teal-100 text-teal-800"
        title="Environmental Conditions"
        subtitle="Atmospheric telemetry, micro-climate dynamics, and abiotic stress risk"
        badge={
          <span className="text-xs font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
            7 Parameters
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Temperature */}
        <InputWithUnit
          label="Temperature"
          unit="°C"
          type="number"
          step="any"
          requiredStar
          placeholder="25"
          value={formData.temperature ?? ''}
          error={errors.temperature}
          onChange={(e) => handleNumericChange('temperature', e.target.value)}
        />

        {/* Humidity */}
        <InputWithUnit
          label="Humidity"
          unit="%"
          type="number"
          step="any"
          requiredStar
          placeholder="80"
          value={formData.humidity ?? ''}
          error={errors.humidity}
          onChange={(e) => handleNumericChange('humidity', e.target.value)}
        />

        {/* Rainfall */}
        <InputWithUnit
          label="Rainfall"
          unit="mm"
          type="number"
          step="any"
          requiredStar
          placeholder="200"
          value={formData.rainfall ?? ''}
          error={errors.rainfall}
          onChange={(e) => handleNumericChange('rainfall', e.target.value)}
        />

        {/* Sunlight Exposure */}
        <InputWithUnit
          label="Sunlight Exposure"
          unit="hours"
          type="number"
          step="any"
          requiredStar
          placeholder="8"
          value={formData.sunlight_exposure ?? ''}
          error={errors.sunlight_exposure}
          onChange={(e) => handleNumericChange('sunlight_exposure', e.target.value)}
        />

        {/* Wind Speed */}
        <InputWithUnit
          label="Wind Speed"
          unit="m/s"
          type="number"
          step="any"
          requiredStar
          placeholder="3.5"
          value={formData.wind_speed ?? ''}
          error={errors.wind_speed}
          onChange={(e) => handleNumericChange('wind_speed', e.target.value)}
        />

        {/* CO2 Concentration */}
        <InputWithUnit
          label="CO₂ Concentration"
          unit="ppm"
          type="number"
          step="any"
          requiredStar
          placeholder="400"
          value={formData.co2_concentration ?? ''}
          error={errors.co2_concentration}
          onChange={(e) => handleNumericChange('co2_concentration', e.target.value)}
        />

        {/* Frost Risk (Col 1) */}
        <InputWithUnit
          label="Frost Risk"
          unit="%"
          type="number"
          step="any"
          requiredStar
          placeholder="5"
          value={formData.frost_risk ?? ''}
          error={errors.frost_risk}
          helperText="Hazard threshold: > 20% triggers frost mitigation"
          onChange={(e) => handleNumericChange('frost_risk', e.target.value)}
        />

        {/* Telemetry Callout Card (Spans 2 columns to fill row 3 seamlessly) */}
        <div className="sm:col-span-2 flex items-start gap-3.5 p-4 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
            <SatelliteDish className="w-5 h-5 text-emerald-700" />
          </div>
          <div>
            <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider mb-1">
              Real-Time Atmospheric Telemetry
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Temperature, humidity, wind, and rainfall can be synchronized live from the Open-Meteo API using the <strong>Live Weather</strong> tool in the Farm Context section above.
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}
