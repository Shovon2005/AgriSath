import { FarmInputs } from './schemas';

export interface ProbabilityItem {
  crop: string;
  probability: number;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  direction?: 'positive' | 'negative' | 'neutral';
  explanation?: string;
}

export interface ShapWaterfall {
  base_value: number;
  prediction_value: number;
  driving_factors: {
    feature: string;
    value: number | string;
    contribution: number;
    direction: 'positive' | 'negative';
  }[];
}

export interface PredictionResult {
  recommended_crop: string;
  confidence: number;
  probabilities: ProbabilityItem[];
  important_features: FeatureImportanceItem[];
  top_3_crops?: {
    rank: number;
    crop: string;
    confidence: number;
    suitability_score?: number;
    water_match?: string;
    season_alignment?: string;
    yield_potential?: string;
    growth_duration_days?: number;
  }[];
  waterfall?: ShapWaterfall;
  comparison_matrix?: {
    crops: string[];
    attributes: {
      name: string;
      values: Record<string, string | number>;
    }[];
  };
}

export interface SoilHealthResult {
  fertility_class: 'High' | 'Medium' | 'Low';
  soil_score: number;
  status: string;
  ph_status: string;
  ph_recommendation: string;
  organic_carbon_status: string;
  salinity_hazard: string;
  deficiencies: string[];
  excesses: string[];
  improvement_actions: string[];
}

export interface IrrigationResult {
  irrigation_required: string;
  priority: 'High' | 'Medium' | 'Low';
  daily_water_requirement_mm: number;
  total_farm_litres: number;
  total_cubic_meters: number;
  next_irrigation_time: string;
  recommendations: string[];
  rainfall_postponed?: boolean;
}

export interface CommercialFertilizers {
  urea_kg_ha: number;
  dap_kg_ha: number;
  mop_kg_ha: number;
  urea_bags_farm?: number;
  dap_bags_farm?: number;
  mop_bags_farm?: number;
}

export interface FertilizerResult {
  commercial_fertilizers: CommercialFertilizers;
  target_deficits: {
    N_deficit_kg_ha: number;
    P_deficit_kg_ha: number;
    K_deficit_kg_ha: number;
  };
  schedule_splits: {
    basal: Record<string, number>;
    vegetative: Record<string, number>;
    flowering: Record<string, number>;
  };
  organic_alternatives: string[];
  recommendations: string[];
}

export interface HazardRiskResult {
  overall_risk_level: 'High' | 'Medium' | 'Low';
  active_hazards: {
    hazard: string;
    severity: 'High' | 'Medium' | 'Low';
    trigger: string;
    mitigation: string;
  }[];
  risks?: string[];
  recommendations?: string[];
}

export interface AdvisoryResult {
  crop_name: string;
  soil: SoilHealthResult;
  irrigation: IrrigationResult;
  fertilizer: FertilizerResult;
  hazards?: HazardRiskResult;
  risks?: HazardRiskResult;
}

export interface PredictResponse {
  status: 'success' | 'error';
  prediction: PredictionResult;
  advisory: AdvisoryResult;
  record_id?: number;
  sanitized_inputs?: Record<string, any>;
  error?: string;
  message?: string;
  details?: Record<string, string>;
}

export interface WhatIfResponse {
  status: 'success' | 'error';
  baseline_prediction: {
    crop: string;
    confidence: number;
  };
  simulated_prediction: {
    crop: string;
    confidence: number;
    probabilities: ProbabilityItem[];
  };
  crop_changed: boolean;
  confidence_delta: number;
  top_feature_changes: {
    feature: string;
    old_value: any;
    new_value: any;
  }[];
}

export interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  wind_speed: number;
  expected_rainfall_24h: number;
  source: string;
}

export interface WeatherResponse {
  status: 'success' | 'error';
  weather?: WeatherData;
  error?: string;
}

export interface HistoryRecord {
  id: number;
  timestamp: string;
  crop: string;
  confidence: number;
  location: string;
  season: string;
  farm_area: number;
  fertility_class: 'High' | 'Medium' | 'Low';
  soil_score: number;
  irrigation_priority: 'High' | 'Medium' | 'Low';
  inputs?: Record<string, any>;
  advisory_summary?: Record<string, any>;
}

export interface HistoryResponse {
  status: 'success' | 'error';
  history: HistoryRecord[];
  total: number;
}
