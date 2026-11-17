import React, { useState } from 'react';
import { MapPin, CloudSun, CheckCircle2, Loader2 } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { InputWithUnit } from '@/components/ui/InputWithUnit';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { FarmInputs } from '@/types/schemas';
import { WeatherData } from '@/types/api';
import { api } from '@/lib/api';

interface FarmContextSectionProps {
  formData: Partial<FarmInputs>;
  errors: Record<string, string>;
  onChange: (field: keyof FarmInputs, value: any) => void;
  onWeatherSync?: (weather: WeatherData) => void;
}

export function FarmContextSection({
  formData,
  errors,
  onChange,
  onWeatherSync,
}: FarmContextSectionProps) {
  const [isFetchingWeather, setIsFetchingWeather] = useState(false);
  const [syncedWeather, setSyncedWeather] = useState<WeatherData | null>(null);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  const handleFetchWeather = async () => {
    setIsFetchingWeather(true);
    setWeatherError(null);
    try {
      const loc = formData.location || 'Local Farm';
      const res = await api.fetchLiveWeather(loc);
      if (res.status === 'success' && res.weather) {
        setSyncedWeather(res.weather);
        if (onWeatherSync) {
          onWeatherSync(res.weather);
        }
      } else {
        setWeatherError('Could not fetch live telemetry. Using manual inputs.');
      }
    } catch (err: any) {
      setWeatherError(err.message || 'Weather service unavailable.');
    } finally {
      setIsFetchingWeather(false);
    }
  };

  const handleNumericChange = (field: keyof FarmInputs, rawVal: string) => {
    if (rawVal === '') {
      onChange(field, undefined);
      return;
    }
    const num = parseFloat(rawVal);
    onChange(field, isNaN(num) ? rawVal : num);
  };

  return (
    <Card className="border-sky-100">
      <CardHeader
        icon={<MapPin className="w-5 h-5" />}
        iconBgClass="bg-sky-100 text-sky-800"
        title="Farm Scale & Location Context"
        subtitle="Geographic zoning, cropping season, acreage, and real-time atmospheric synchronization"
        badge={
          <span className="text-xs font-bold text-sky-700 bg-sky-50 px-3 py-1 rounded-full border border-sky-200">
            5 Parameters
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Farm Location with Live Weather Button (Spans 2 columns) */}
        <div className="sm:col-span-2 flex flex-col gap-1.5">
          <label
            htmlFor="farm-location-input"
            className="text-xs font-bold text-slate-800 flex items-center justify-between"
          >
            <span>
              Farm Location / District <span className="text-rose-600 font-semibold">*</span>
            </span>
          </label>

          <div className="flex gap-2.5">
            <input
              id="farm-location-input"
              type="text"
              className="flex-1 h-12 bg-white border border-slate-300 rounded-xl px-3.5 text-slate-900 text-sm font-medium focus:border-agri-600 focus:ring-4 focus:ring-agri-600/15 outline-none transition-all"
              placeholder="e.g. Punjab, West Bengal, Maharashtra, Delhi"
              value={formData.location || ''}
              onChange={(e) => onChange('location', e.target.value)}
            />
            <Button
              type="button"
              variant="primary"
              size="md"
              isLoading={isFetchingWeather}
              leftIcon={<CloudSun className="w-4 h-4" />}
              onClick={handleFetchWeather}
              className="shrink-0"
            >
              Live Weather
            </Button>
          </div>

          {syncedWeather && (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mt-1">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>
                Synced for {syncedWeather.location}: {syncedWeather.temperature}°C, {syncedWeather.humidity}% RH, Rain: {syncedWeather.rainfall}mm, Forecast: {syncedWeather.expected_rainfall_24h}mm ({syncedWeather.source})
              </span>
            </div>
          )}

          {weatherError && (
            <span className="text-xs text-rose-600 font-medium mt-1">
              {weatherError}
            </span>
          )}
        </div>

        {/* Cropping Season */}
        <Select
          label="Cropping Season"
          requiredStar
          value={formData.season || 'Whole Year'}
          error={errors.season}
          options={[
            { value: 'Kharif', label: 'Kharif (Monsoon / Autumn)' },
            { value: 'Rabi', label: 'Rabi (Winter / Spring)' },
            { value: 'Zaid', label: 'Zaid (Summer)' },
            { value: 'Whole Year', label: 'Whole Year / Perennial' },
          ]}
          onChange={(e) => onChange('season', e.target.value as any)}
        />

        {/* Farm Area Size */}
        <InputWithUnit
          label="Farm Area Size"
          type="number"
          step="0.01"
          requiredStar
          placeholder="1.0"
          value={formData.farm_area ?? ''}
          error={errors.farm_area}
          onChange={(e) => handleNumericChange('farm_area', e.target.value)}
        />

        {/* Area Unit */}
        <Select
          label="Area Unit"
          requiredStar
          value={formData.farm_area_unit || 'hectare'}
          error={errors.farm_area_unit}
          options={[
            { value: 'hectare', label: 'Hectare (ha)' },
            { value: 'acre', label: 'Acre' },
          ]}
          onChange={(e) => onChange('farm_area_unit', e.target.value as any)}
        />

        {/* Expected Rain (24-48h) */}
        <InputWithUnit
          label="Expected Rain (24-48h)"
          unit="mm"
          type="number"
          step="any"
          placeholder="0.0"
          value={formData.expected_rainfall_24h ?? ''}
          error={errors.expected_rainfall_24h}
          helperText="Automated irrigation postponement trigger"
          onChange={(e) => handleNumericChange('expected_rainfall_24h', e.target.value)}
        />
      </div>
    </Card>
  );
}
