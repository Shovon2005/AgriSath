import React from 'react';
import { Tractor, Calculator } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { InputWithUnit } from '@/components/ui/InputWithUnit';
import { Select } from '@/components/ui/Select';
import { FarmInputs } from '@/types/schemas';

interface FarmManagementSectionProps {
  formData: Partial<FarmInputs>;
  errors: Record<string, string>;
  onChange: (field: keyof FarmInputs, value: any) => void;
}

export function FarmManagementSection({
  formData,
  errors,
  onChange,
}: FarmManagementSectionProps) {
  const handleNumericChange = (field: keyof FarmInputs, rawVal: string) => {
    if (rawVal === '') {
      onChange(field, undefined);
      return;
    }
    const num = parseFloat(rawVal);
    onChange(field, isNaN(num) ? rawVal : num);
  };

  return (
    <Card className="border-emerald-100">
      <CardHeader
        icon={<Tractor className="w-5 h-5" />}
        iconBgClass="bg-emerald-100 text-emerald-800"
        title="Farm Management & Practices"
        subtitle="Irrigation frequency, plant density, fertilizer dosage, and agronomic management"
        badge={
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
            8 Parameters
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Irrigation Frequency */}
        <InputWithUnit
          label="Irrigation Frequency"
          unit="times/wk"
          type="number"
          step="any"
          requiredStar
          placeholder="3"
          value={formData.irrigation_frequency ?? ''}
          error={errors.irrigation_frequency}
          onChange={(e) => handleNumericChange('irrigation_frequency', e.target.value)}
        />

        {/* Crop Density */}
        <InputWithUnit
          label="Crop Density"
          unit="%"
          type="number"
          step="any"
          requiredStar
          placeholder="70"
          value={formData.crop_density ?? ''}
          error={errors.crop_density}
          onChange={(e) => handleNumericChange('crop_density', e.target.value)}
        />

        {/* Pest Pressure */}
        <InputWithUnit
          label="Pest Pressure"
          unit="%"
          type="number"
          step="any"
          requiredStar
          placeholder="20"
          value={formData.pest_pressure ?? ''}
          error={errors.pest_pressure}
          helperText="Hazard threshold: > 40% triggers pest advisory"
          onChange={(e) => handleNumericChange('pest_pressure', e.target.value)}
        />

        {/* Fertilizer Usage */}
        <InputWithUnit
          label="Fertilizer Usage"
          unit="kg/ha"
          type="number"
          step="any"
          requiredStar
          placeholder="50"
          value={formData.fertilizer_usage ?? ''}
          error={errors.fertilizer_usage}
          onChange={(e) => handleNumericChange('fertilizer_usage', e.target.value)}
        />

        {/* Growth Stage */}
        <Select
          label="Growth Stage"
          requiredStar
          value={formData.growth_stage || ''}
          error={errors.growth_stage}
          options={[
            { value: '', label: 'Select Growth Stage' },
            { value: 'Seedling', label: 'Seedling Stage (Initial Kc)' },
            { value: 'Vegetative', label: 'Vegetative Stage (Mid-Season Kc)' },
            { value: 'Flowering', label: 'Flowering Stage (Peak Kc)' },
            { value: 'Maturity', label: 'Maturity / Ripening Stage' },
          ]}
          onChange={(e) => onChange('growth_stage', e.target.value as any)}
        />

        {/* Water Source Type */}
        <Select
          label="Water Source Type"
          requiredStar
          value={formData.water_source_type || ''}
          error={errors.water_source_type}
          options={[
            { value: '', label: 'Select Water Source' },
            { value: 'Groundwater', label: 'Groundwater (Borewell / Tubewell)' },
            { value: 'Rainwater', label: 'Rainwater Harvesting' },
            { value: 'Canal', label: 'Canal Irrigation' },
            { value: 'River', label: 'River / Surface Water' },
          ]}
          onChange={(e) => onChange('water_source_type', e.target.value as any)}
        />

        {/* Urban Area Proximity */}
        <InputWithUnit
          label="Urban Area Proximity"
          unit="km"
          type="number"
          step="any"
          requiredStar
          placeholder="10"
          value={formData.urban_area_proximity ?? ''}
          error={errors.urban_area_proximity}
          onChange={(e) => handleNumericChange('urban_area_proximity', e.target.value)}
        />

        {/* Water Usage Efficiency */}
        <InputWithUnit
          label="Water Usage Efficiency"
          unit="ratio"
          type="number"
          step="any"
          requiredStar
          placeholder="1.2"
          value={formData.water_usage_efficiency ?? ''}
          error={errors.water_usage_efficiency}
          onChange={(e) => handleNumericChange('water_usage_efficiency', e.target.value)}
        />

        {/* Agronomic Decision Matrix Info Card (Fills Col 3 seamlessly) */}
        <div className="flex items-start gap-3.5 p-4 rounded-xl bg-slate-50 border border-slate-200/80">
          <div className="w-9 h-9 rounded-lg bg-sky-100 text-sky-800 flex items-center justify-center shrink-0">
            <Calculator className="w-5 h-5 text-sky-700" />
          </div>
          <div>
            <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider mb-1">
              Agronomic Calibration
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Growth stage and water efficiency calibrate commercial fertilizer splits, irrigation ETc, and localized risk scores.
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}
