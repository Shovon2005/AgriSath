import React from 'react';
import { Mountain } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { InputWithUnit } from '@/components/ui/InputWithUnit';
import { Select } from '@/components/ui/Select';
import { FarmInputs } from '@/types/schemas';

interface SoilParametersSectionProps {
  formData: Partial<FarmInputs>;
  errors: Record<string, string>;
  onChange: (field: keyof FarmInputs, value: any) => void;
}

export function SoilParametersSection({
  formData,
  errors,
  onChange,
}: SoilParametersSectionProps) {
  const handleNumericChange = (field: keyof FarmInputs, rawVal: string) => {
    if (rawVal === '') {
      onChange(field, undefined);
      return;
    }
    const num = parseFloat(rawVal);
    onChange(field, isNaN(num) ? rawVal : num);

    // Auto-calculate Organic Matter from Organic Carbon if OM is unedited
    if (field === 'organic_carbon' && !isNaN(num)) {
      const omEst = parseFloat((num * 1.724).toFixed(2));
      onChange('organic_matter', omEst);
    }
  };

  return (
    <Card className="border-emerald-100">
      <CardHeader
        icon={<Mountain className="w-5 h-5" />}
        iconBgClass="bg-emerald-100 text-emerald-800"
        title="Soil Parameters"
        subtitle="Chemical composition, soil reaction, and physical fertility properties"
        badge={
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
            9 Parameters
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Nitrogen (N) */}
        <InputWithUnit
          label="Nitrogen (N)"
          unit="mg/kg"
          type="number"
          step="any"
          requiredStar
          placeholder="90"
          value={formData.N ?? ''}
          error={errors.N}
          onChange={(e) => handleNumericChange('N', e.target.value)}
        />

        {/* Phosphorus (P) */}
        <InputWithUnit
          label="Phosphorus (P)"
          unit="mg/kg"
          type="number"
          step="any"
          requiredStar
          placeholder="42"
          value={formData.P ?? ''}
          error={errors.P}
          onChange={(e) => handleNumericChange('P', e.target.value)}
        />

        {/* Potassium (K) */}
        <InputWithUnit
          label="Potassium (K)"
          unit="mg/kg"
          type="number"
          step="any"
          requiredStar
          placeholder="43"
          value={formData.K ?? ''}
          error={errors.K}
          onChange={(e) => handleNumericChange('K', e.target.value)}
        />

        {/* Soil pH */}
        <InputWithUnit
          label="Soil pH"
          unit="pH"
          type="number"
          step="0.01"
          requiredStar
          placeholder="6.5"
          value={formData.ph ?? ''}
          error={errors.ph}
          onChange={(e) => handleNumericChange('ph', e.target.value)}
        />

        {/* Soil Moisture */}
        <InputWithUnit
          label="Soil Moisture"
          unit="%"
          type="number"
          step="any"
          optionalTag
          placeholder="35 (defaults to 30%)"
          value={formData.soil_moisture ?? ''}
          error={errors.soil_moisture}
          onChange={(e) => handleNumericChange('soil_moisture', e.target.value)}
        />

        {/* Soil Type */}
        <Select
          label="Soil Type"
          requiredStar
          value={formData.soil_type || ''}
          error={errors.soil_type}
          options={[
            { value: '', label: 'Select Soil Type' },
            { value: 'Loamy', label: 'Loamy (Balanced)' },
            { value: 'Clay', label: 'Clay (High Moisture Retention)' },
            { value: 'Sandy', label: 'Sandy (Light / High Drainage)' },
          ]}
          onChange={(e) => onChange('soil_type', e.target.value as any)}
        />

        {/* Organic Carbon (OC) */}
        <InputWithUnit
          label="Organic Carbon (OC)"
          unit="%"
          type="number"
          step="0.01"
          placeholder="0.75"
          value={formData.organic_carbon ?? ''}
          error={errors.organic_carbon}
          helperText="Standard soil carbon fraction"
          onChange={(e) => handleNumericChange('organic_carbon', e.target.value)}
        />

        {/* Organic Matter (OM) */}
        <InputWithUnit
          label="Organic Matter (OM)"
          unit="%"
          type="number"
          step="0.01"
          placeholder="3.5"
          value={formData.organic_matter ?? ''}
          error={errors.organic_matter}
          helperText="Derived as OM = 1.724 × OC"
          onChange={(e) => handleNumericChange('organic_matter', e.target.value)}
        />

        {/* Electrical Conductivity (EC) */}
        <InputWithUnit
          label="Electrical Conductivity (EC)"
          unit="dS/m"
          type="number"
          step="0.01"
          placeholder="0.6"
          value={formData.electrical_conductivity ?? ''}
          error={errors.electrical_conductivity}
          helperText="Salinity hazard diagnostic"
          onChange={(e) => handleNumericChange('electrical_conductivity', e.target.value)}
        />
      </div>
    </Card>
  );
}
