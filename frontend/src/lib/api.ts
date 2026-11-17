/**
 * AgriSathi API Service Layer.
 * Provides type-safe async functions to communicate with the Flask Python backend.
 */

import {
  FarmInputs,
  PredictResponse,
  WhatIfResponse,
  WeatherResponse,
  HistoryResponse,
  HistoryRecord,
} from '@/types/api';

const BASE_URL = typeof window !== 'undefined'
  ? '' // Uses Next.js proxy rewrites in browser
  : (process.env.BACKEND_API_URL || 'http://127.0.0.1:5001');

async function handleResponse<T>(res: Response): Promise<T> {
  const contentType = res.headers.get('content-type') || '';
  if (!res.ok) {
    if (contentType.includes('application/json')) {
      const errJson = await res.json();
      throw new Error(errJson.message || errJson.error || `HTTP error ${res.status}`);
    }
    const text = await res.text();
    throw new Error(text || `HTTP error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  /**
   * Health check to ensure model and backend services are operational.
   */
  async checkHealth(): Promise<{ status: string; model_loaded: boolean; version: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/health`, { method: 'GET' });
    return handleResponse(res);
  },

  /**
   * Fetch predefined farm scenarios (Wetland Rice, Semi-Arid Chickpea, etc.).
   */
  async fetchScenarios(): Promise<Record<string, any>> {
    const res = await fetch(`${BASE_URL}/api/v1/scenarios`, { method: 'GET' });
    const data = await handleResponse<{ status: string; scenarios: Record<string, any> }>(res);
    return data.scenarios || {};
  },

  /**
   * Run full ML prediction pipeline and agronomic advisory engines.
   */
  async predictCrop(inputs: Partial<FarmInputs>): Promise<PredictResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(inputs),
    });
    return handleResponse<PredictResponse>(res);
  },

  /**
   * Fetch live weather data via Open-Meteo API.
   */
  async fetchLiveWeather(location: string = 'Local Farm'): Promise<WeatherResponse> {
    const url = `${BASE_URL}/api/v1/weather?location=${encodeURIComponent(location)}`;
    const res = await fetch(url, { method: 'GET' });
    return handleResponse<WeatherResponse>(res);
  },

  /**
   * Simulate a What-If scenario with parameter perturbations.
   */
  async simulateWhatIf(
    baseline: Record<string, any>,
    perturbations: Record<string, any>
  ): Promise<WhatIfResponse> {
    const res = await fetch(`${BASE_URL}/api/v1/what-if`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        baseline,
        perturbations,
      }),
    });
    return handleResponse<WhatIfResponse>(res);
  },

  /**
   * Fetch historical prediction records with optional crop filter.
   */
  async fetchHistory(crop?: string, limit: number = 50): Promise<HistoryResponse> {
    const params = new URLSearchParams();
    if (crop) params.set('crop', crop);
    params.set('limit', limit.toString());

    const res = await fetch(`${BASE_URL}/api/v1/history?${params.toString()}`, {
      method: 'GET',
    });
    return handleResponse<HistoryResponse>(res);
  },

  /**
   * Fetch single historical record details by record ID.
   */
  async fetchHistoryDetail(recordId: number): Promise<{ status: string; record: HistoryRecord }> {
    const res = await fetch(`${BASE_URL}/api/v1/history/${recordId}`, {
      method: 'GET',
    });
    return handleResponse(res);
  },

  /**
   * Download official PDF report as a binary blob and trigger browser download.
   */
  async downloadReportPdf(inputs: Record<string, any>, filename: string = 'agrisathi_advisory_report.pdf'): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/v1/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(inputs),
    });

    if (!res.ok) {
      throw new Error(`Failed to generate PDF: ${res.statusText}`);
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};
