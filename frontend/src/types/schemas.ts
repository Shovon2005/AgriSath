/**
 * AgriSathi Precision Agriculture Domain Schemas and TypeScript Interfaces.
 * Mirrors agrisathi.core.schemas with strict types and runtime helpers.
 */

export interface FarmInputs {
  // Macronutrients
  N: number;
  P: number;
  K: number;

  // Soil Chemical & Physical
  ph: number;
  soil_moisture?: number;
  soil_type: 'Loamy' | 'Clay' | 'Sandy';
  organic_carbon?: number;
  organic_matter?: number;
  electrical_conductivity?: number;

  // Farm Context & Geography
  location?: string;
  season?: 'Kharif' | 'Rabi' | 'Zaid' | 'Whole Year';
  farm_area?: number;
  farm_area_unit?: 'hectare' | 'acre';
  expected_rainfall_24h?: number;

  // Environmental Telemetry
  temperature: number;
  humidity: number;
  rainfall: number;
  sunlight_exposure: number;
  wind_speed: number;
  co2_concentration: number;
  frost_risk: number;

  // Farm Practices & Water Management
  irrigation_frequency: number;
  crop_density: number;
  pest_pressure: number;
  fertilizer_usage: number;
  growth_stage: 'Seedling' | 'Vegetative' | 'Flowering' | 'Maturity';
  water_source_type: 'Groundwater' | 'Rainwater' | 'Canal' | 'River';
  urban_area_proximity: number;
  water_usage_efficiency: number;
}

export interface FeatureMetadata {
  displayName: string;
  unit: string;
  min: number;
  max: number;
  step?: number;
  placeholder?: string;
  category: 'soil' | 'context' | 'environment' | 'management';
}

export const FEATURE_METADATA: Record<string, FeatureMetadata> = {
  N: { displayName: 'Nitrogen (N)', unit: 'mg/kg', min: 0, max: 300, step: 1, placeholder: '90', category: 'soil' },
  P: { displayName: 'Phosphorus (P)', unit: 'mg/kg', min: 0, max: 200, step: 1, placeholder: '42', category: 'soil' },
  K: { displayName: 'Potassium (K)', unit: 'mg/kg', min: 0, max: 300, step: 1, placeholder: '43', category: 'soil' },
  ph: { displayName: 'Soil pH', unit: 'pH', min: 0, max: 14, step: 0.1, placeholder: '6.5', category: 'soil' },
  soil_moisture: { displayName: 'Soil Moisture', unit: '%', min: 0, max: 100, step: 1, placeholder: '35', category: 'soil' },
  organic_carbon: { displayName: 'Organic Carbon (OC)', unit: '%', min: 0, max: 10, step: 0.01, placeholder: '0.75', category: 'soil' },
  organic_matter: { displayName: 'Organic Matter (OM)', unit: '%', min: 0, max: 15, step: 0.1, placeholder: '3.5', category: 'soil' },
  electrical_conductivity: { displayName: 'Electrical Conductivity (EC)', unit: 'dS/m', min: 0, max: 20, step: 0.01, placeholder: '0.6', category: 'soil' },

  farm_area: { displayName: 'Farm Area Size', unit: 'ha', min: 0.01, max: 10000, step: 0.1, placeholder: '1.0', category: 'context' },
  expected_rainfall_24h: { displayName: 'Expected Rain (24-48h)', unit: 'mm', min: 0, max: 1000, step: 1, placeholder: '0.0', category: 'context' },

  temperature: { displayName: 'Temperature', unit: '°C', min: -10, max: 60, step: 0.5, placeholder: '25', category: 'environment' },
  humidity: { displayName: 'Humidity', unit: '%', min: 0, max: 100, step: 1, placeholder: '80', category: 'environment' },
  rainfall: { displayName: 'Rainfall', unit: 'mm', min: 0, max: 1000, step: 1, placeholder: '200', category: 'environment' },
  sunlight_exposure: { displayName: 'Sunlight Exposure', unit: 'hours', min: 0, max: 24, step: 0.5, placeholder: '8', category: 'environment' },
  wind_speed: { displayName: 'Wind Speed', unit: 'm/s', min: 0, max: 50, step: 0.5, placeholder: '3.5', category: 'environment' },
  co2_concentration: { displayName: 'CO₂ Concentration', unit: 'ppm', min: 100, max: 2000, step: 10, placeholder: '400', category: 'environment' },
  frost_risk: { displayName: 'Frost Risk', unit: '%', min: 0, max: 100, step: 1, placeholder: '5', category: 'environment' },

  irrigation_frequency: { displayName: 'Irrigation Frequency', unit: 'times/wk', min: 0, max: 30, step: 1, placeholder: '3', category: 'management' },
  crop_density: { displayName: 'Crop Density', unit: '%', min: 0, max: 100, step: 1, placeholder: '70', category: 'management' },
  pest_pressure: { displayName: 'Pest Pressure', unit: '%', min: 0, max: 100, step: 1, placeholder: '20', category: 'management' },
  fertilizer_usage: { displayName: 'Fertilizer Usage', unit: 'kg/ha', min: 0, max: 2000, step: 10, placeholder: '50', category: 'management' },
  urban_area_proximity: { displayName: 'Urban Area Proximity', unit: 'km', min: 0, max: 200, step: 1, placeholder: '10', category: 'management' },
  water_usage_efficiency: { displayName: 'Water Usage Efficiency', unit: 'ratio', min: 0, max: 10, step: 0.1, placeholder: '1.2', category: 'management' },
};
