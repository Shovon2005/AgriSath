'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Brain, AlertCircle, Loader2 } from 'lucide-react';
import { ScenarioPresetsBar, ScenarioItem } from '@/components/form/ScenarioPresetsBar';
import { SoilParametersSection } from '@/components/form/SoilParametersSection';
import { FarmContextSection } from '@/components/form/FarmContextSection';
import { EnvironmentalSection } from '@/components/form/EnvironmentalSection';
import { FarmManagementSection } from '@/components/form/FarmManagementSection';
import { PredictActionBar } from '@/components/form/PredictActionBar';
import { FarmInputs } from '@/types/schemas';
import { WeatherData } from '@/types/api';
import { api } from '@/lib/api';

const BASELINE_RICE_PARAMS: Partial<FarmInputs> = {
  N: 90,
  P: 42,
  K: 43,
  ph: 6.5,
  soil_moisture: 30,
  soil_type: 'Clay',
  organic_carbon: 0.85,
  organic_matter: 3.2,
  electrical_conductivity: 0.5,
  location: 'West Bengal, India',
  season: 'Kharif',
  farm_area: 2.5,
  farm_area_unit: 'hectare',
  expected_rainfall_24h: 0.0,
  temperature: 21.0,
  humidity: 82.0,
  rainfall: 202.0,
  sunlight_exposure: 8.5,
  wind_speed: 10.0,
  co2_concentration: 435.0,
  frost_risk: 5.0,
  irrigation_frequency: 4,
  crop_density: 12.0,
  pest_pressure: 55.0,
  fertilizer_usage: 180.0,
  growth_stage: 'Vegetative',
  water_source_type: 'Canal',
  urban_area_proximity: 15.0,
  water_usage_efficiency: 1.2,
};

function HomePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [scenarios, setScenarios] = useState<Record<string, ScenarioItem>>({});
  const [formData, setFormData] = useState<Partial<FarmInputs>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Fetch scenarios on load
  useEffect(() => {
    async function loadScenarios() {
      try {
        const data = await api.fetchScenarios();
        setScenarios(data);

        // Check if ?demo=key in URL
        const demoKey = searchParams.get('demo');
        if (demoKey && data[demoKey]) {
          setFormData(data[demoKey].parameters);
          setActivePreset(demoKey);
        }
      } catch (err) {
        console.warn('Could not load dynamic scenarios:', err);
      }
    }
    loadScenarios();
  }, [searchParams]);

  const handleFieldChange = (field: keyof FarmInputs, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSelectPreset = (scenario: ScenarioItem) => {
    setFormData(scenario.parameters);
    setActivePreset(scenario.key);
    setErrors({});
    setSubmitError(null);
  };

  const handleFillBaseline = () => {
    setFormData(BASELINE_RICE_PARAMS);
    setActivePreset('rice');
    setErrors({});
    setSubmitError(null);
  };

  const handleReset = () => {
    setFormData({});
    setActivePreset(null);
    setErrors({});
    setSubmitError(null);
  };

  const handleWeatherSync = (weather: WeatherData) => {
    setFormData((prev) => ({
      ...prev,
      temperature: weather.temperature,
      humidity: weather.humidity,
      rainfall: weather.rainfall,
      wind_speed: weather.wind_speed,
      expected_rainfall_24h: weather.expected_rainfall_24h,
    }));
  };

  const validateForm = (): boolean => {
    const requiredFields: (keyof FarmInputs)[] = [
      'N',
      'P',
      'K',
      'ph',
      'soil_type',
      'temperature',
      'humidity',
      'rainfall',
      'sunlight_exposure',
      'wind_speed',
      'co2_concentration',
      'frost_risk',
      'irrigation_frequency',
      'crop_density',
      'pest_pressure',
      'fertilizer_usage',
      'growth_stage',
      'water_source_type',
      'urban_area_proximity',
      'water_usage_efficiency',
    ];

    const newErrors: Record<string, string> = {};
    for (const f of requiredFields) {
      const val = formData[f];
      if (val === undefined || val === null || val === '') {
        newErrors[f] = 'Required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    if (!validateForm()) {
      setSubmitError('Please fill in all required agronomic parameters, or click "Auto-Fill Baseline" above.');
      window.scrollTo({ top: 380, behavior: 'smooth' });
      return;
    }

    setIsLoading(true);
    try {
      const res = await api.predictCrop(formData);
      if (res.status === 'success') {
        sessionStorage.setItem('agrisathi_latest_prediction', JSON.stringify(res));
        sessionStorage.setItem('agrisathi_latest_inputs', JSON.stringify(formData));
        router.push('/result');
      } else {
        setSubmitError(res.message || 'Prediction failed. Please verify input values.');
      }
    } catch (err: any) {
      setSubmitError(err.message || 'Network error connecting to decision support engine.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Hero Section */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 py-4 mb-2">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/80 text-emerald-800 text-xs font-bold mb-4 border border-emerald-200">
            <Brain className="w-3.5 h-3.5 text-emerald-700" />
            <span>Explainable AI-Powered Decision Support</span>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-[1.15] mb-4">
            Smart Farming.<br />
            <span className="text-agri-700">Better Decisions.</span>
          </h1>
          <p className="text-sm sm:text-base text-slate-600 font-medium leading-relaxed">
            Multi-crop recommendation, soil reaction diagnosis, smart irrigation scheduling (ETc), and commercial fertilizer dosing with local SHAP XAI explainability.
          </p>
        </div>

        <div className="hidden lg:flex flex-col gap-3 p-5 rounded-2xl bg-white border border-emerald-100 shadow-soft shrink-0 w-80">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Model Capabilities</div>
          <div className="grid grid-cols-3 gap-2 text-center pt-2">
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="block text-xl font-extrabold text-agri-800">22+</span>
              <span className="text-[11px] font-bold text-slate-500">Crops</span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="block text-xl font-extrabold text-agri-800">22</span>
              <span className="text-[11px] font-bold text-slate-500">Features</span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="block text-xl font-extrabold text-agri-800">&lt;10ms</span>
              <span className="text-[11px] font-bold text-slate-500">SHAP XAI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Scenario Presets Bar */}
      <ScenarioPresetsBar
        scenarios={scenarios}
        activePreset={activePreset}
        onSelectPreset={handleSelectPreset}
        onFillBaseline={handleFillBaseline}
        onReset={handleReset}
      />

      {/* Validation Error Banner */}
      {submitError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm font-semibold flex items-center gap-3 shadow-xs">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{submitError}</span>
        </div>
      )}

      {/* Main 4-Section Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-6" noValidate>
        {/* Section 1: Soil */}
        <SoilParametersSection
          formData={formData}
          errors={errors}
          onChange={handleFieldChange}
        />

        {/* Section 2: Farm Context & Scale */}
        <FarmContextSection
          formData={formData}
          errors={errors}
          onChange={handleFieldChange}
          onWeatherSync={handleWeatherSync}
        />

        {/* Section 3: Environmental Conditions */}
        <EnvironmentalSection
          formData={formData}
          errors={errors}
          onChange={handleFieldChange}
        />

        {/* Section 4: Farm Management */}
        <FarmManagementSection
          formData={formData}
          errors={errors}
          onChange={handleFieldChange}
        />

        {/* Predict CTA Bar */}
        <PredictActionBar isLoading={isLoading} />
      </form>
    </div>
  );
}

export default function HomePage() {
  return (
    <React.Suspense
      fallback={
        <div className="py-24 text-center text-slate-500 flex flex-col items-center justify-center gap-2">
          <Loader2 className="w-8 h-8 animate-spin text-agri-600" />
          <span className="text-xs font-semibold">Initializing Decision Engine...</span>
        </div>
      }
    >
      <HomePageContent />
    </React.Suspense>
  );
}
