'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  History,
  Search,
  FileDown,
  Eye,
  Calendar,
  Clock,
  MapPin,
  Sprout,
  PlusCircle,
  RotateCcw,
  X,
  ChevronRight,
  Droplets,
  Mountain,
  FlaskConical,
  AlertCircle,
  Sliders,
} from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Button } from '@/components/ui/Button';
import { HistoryRecord } from '@/types/api';
import { api } from '@/lib/api';

const CROP_PILLS = ['All Crops', 'Rice', 'Chickpea', 'Cotton', 'Maize', 'Papaya', 'Jute'];

export default function HistoryPage() {
  const router = useRouter();
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<string>('All Crops');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<HistoryRecord | null>(null);
  const [isOpeningResult, setIsOpeningResult] = useState<boolean>(false);

  const loadHistory = async (cropFilter?: string) => {
    setIsLoading(true);
    try {
      const crop = cropFilter && cropFilter !== 'All Crops' ? cropFilter.toLowerCase() : undefined;
      const res = await api.fetchHistory(crop);
      if (res.status === 'success') {
        setRecords(res.history || []);
      }
    } catch (e) {
      console.error('Error fetching history:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(selectedCrop);
  }, [selectedCrop]);

  const handleDownloadPdf = async (item: HistoryRecord) => {
    if (!item.inputs) {
      alert('Record inputs not available for PDF export.');
      return;
    }
    setDownloadingId(item.id);
    try {
      await api.downloadReportPdf(item.inputs, `agrisathi_report_${item.id}_${item.crop.toLowerCase()}.pdf`);
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleInspectInDashboard = async (item: HistoryRecord) => {
    if (!item.inputs) {
      alert('Record farm parameters not available.');
      return;
    }
    setIsOpeningResult(true);
    try {
      const res = await api.predictCrop(item.inputs as any);
      if (res.status === 'success') {
        sessionStorage.setItem('agrisathi_latest_prediction', JSON.stringify(res));
        sessionStorage.setItem('agrisathi_latest_inputs', JSON.stringify(res.sanitized_inputs || item.inputs));
        router.push('/result');
      } else {
        alert('Could not inspect advisory: ' + (res.message || 'Unknown error'));
      }
    } catch (err: any) {
      alert('Failed to load assessment in dashboard: ' + err.message);
    } finally {
      setIsOpeningResult(false);
    }
  };

  // Filter records in memory by search query
  const filteredRecords = records.filter((r) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      r.crop.toLowerCase().includes(q) ||
      r.location.toLowerCase().includes(q) ||
      `#${r.id}`.includes(q) ||
      r.season.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/80 text-emerald-800 text-xs font-bold mb-2 border border-emerald-200">
            <History className="w-3.5 h-3.5 text-emerald-700" />
            <span>Agronomic Audit Archive</span>
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">
            Saved Assessments &amp; Historical Advisory
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 font-medium">
            Review past soil health metrics, AI recommendations, irrigation requirements, and export official PDF documents.
          </p>
        </div>

        <Link href="/">
          <Button variant="primary" size="md" leftIcon={<PlusCircle className="w-4 h-4" />}>
            New Farm Advisory
          </Button>
        </Link>
      </div>

      {/* Main Table Card */}
      <Card className="border-slate-200">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-5 mb-5 border-b border-slate-100">
          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by crop, ID, or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-9 pr-3.5 bg-slate-50 border border-slate-300 rounded-xl text-xs sm:text-sm font-medium focus:bg-white focus:border-agri-600 focus:ring-4 focus:ring-agri-600/15 outline-none transition-all"
            />
          </div>

          {/* Crop Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            {CROP_PILLS.map((crop) => (
              <button
                key={crop}
                type="button"
                onClick={() => setSelectedCrop(crop)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all cursor-pointer ${
                  selectedCrop === crop
                    ? 'bg-agri-800 text-white border-agri-800 shadow-sm'
                    : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-emerald-50 hover:border-emerald-300 hover:text-agri-800'
                }`}
              >
                {crop}
              </button>
            ))}
          </div>
        </div>

        {/* Table Content */}
        {isLoading ? (
          <div className="py-20 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
            <RotateCcw className="w-8 h-8 animate-spin text-agri-600" />
            <span className="text-xs font-semibold">Loading historical records...</span>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="py-16 text-center text-slate-400">
            <Sprout className="w-10 h-10 mx-auto mb-2 text-slate-300" />
            <h4 className="text-sm font-bold text-slate-700 mb-1">No Historical Records Found</h4>
            <p className="text-xs text-slate-500">
              {searchQuery ? 'No records match your search filter.' : 'Generate your first farm advisory to save predictions here.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="bg-gradient-to-r from-agri-900 to-agri-800 text-white text-[11px] font-extrabold uppercase tracking-wider">
                  <th className="py-3 px-4 text-center"># ID</th>
                  <th className="py-3 px-4">Date &amp; Time</th>
                  <th className="py-3 px-4">Location &amp; Season</th>
                  <th className="py-3 px-4">Recommended Crop</th>
                  <th className="py-3 px-4 text-center">AI Confidence</th>
                  <th className="py-3 px-4 text-center">Soil Fertility</th>
                  <th className="py-3 px-4 text-center">Irrigation Demand</th>
                  <th className="py-3 px-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
                {filteredRecords.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                    {/* ID */}
                    <td className="py-3.5 px-4 text-center">
                      <span className="font-mono font-bold text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                        #{item.id}
                      </span>
                    </td>

                    {/* Date & Time */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-bold text-slate-900 flex items-center gap-1.5 text-xs">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          {item.timestamp.slice(0, 10)}
                        </span>
                        <span className="text-[11px] text-slate-500 flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          {item.timestamp.slice(11, 16)} UTC
                        </span>
                      </div>
                    </td>

                    {/* Location & Season */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-bold text-slate-900 flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-agri-600 shrink-0" />
                          {item.location}
                        </span>
                        <span className="text-[11px] text-slate-500">
                          {item.season} • {item.farm_area} ha
                        </span>
                      </div>
                    </td>

                    {/* Crop */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-agri-800 font-bold">
                        <Sprout className="w-4 h-4 text-emerald-600" />
                        <span className="capitalize">{item.crop}</span>
                      </div>
                    </td>

                    {/* Confidence */}
                    <td className="py-3.5 px-4 text-center">
                      <div className="flex flex-col items-center gap-1 w-20 mx-auto">
                        <span className="font-extrabold text-agri-800 text-xs">
                          {item.confidence.toFixed(1)}%
                        </span>
                        <ProgressBar value={item.confidence} variant="green" />
                      </div>
                    </td>

                    {/* Soil Fertility */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <Badge
                        variant={item.fertility_class === 'High' ? 'high' : item.fertility_class === 'Medium' ? 'medium' : 'low'}
                        dot
                      >
                        {item.fertility_class} ({item.soil_score}/100)
                      </Badge>
                    </td>

                    {/* Irrigation Demand */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <Badge
                        variant={item.irrigation_priority === 'High' ? 'low' : item.irrigation_priority === 'Medium' ? 'medium' : 'high'}
                      >
                        {item.irrigation_priority} Priority
                      </Badge>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <div className="inline-flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={<Eye className="w-3.5 h-3.5 text-sky-600" />}
                          onClick={() => setSelectedRecord(item)}
                          className="hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700"
                        >
                          Details
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          isLoading={downloadingId === item.id}
                          leftIcon={<FileDown className="w-3.5 h-3.5" />}
                          onClick={() => handleDownloadPdf(item)}
                        >
                          PDF
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="pt-4 mt-4 border-t border-slate-100 flex flex-wrap justify-between items-center text-xs text-slate-500">
          <span>Showing <strong>{filteredRecords.length}</strong> of {records.length} saved assessments</span>
          <span>Click <strong>Details</strong> to inspect agronomic breakdown or <strong>PDF</strong> for official report</span>
        </div>
      </Card>

      {/* Historical Record Details Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gradient-to-r from-agri-900 via-agri-800 to-emerald-900 text-white flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center border border-white/20">
                  <Sprout className="w-6 h-6 text-emerald-300" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-black tracking-tight capitalize">
                      Assessment #{selectedRecord.id} — {selectedRecord.crop}
                    </h3>
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-200 border border-emerald-400/30">
                      {selectedRecord.confidence.toFixed(1)}% Confidence
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 flex items-center gap-2 mt-0.5">
                    <span>{selectedRecord.location}</span>
                    <span>•</span>
                    <span>{selectedRecord.season}</span>
                    <span>•</span>
                    <span>{selectedRecord.farm_area} ha</span>
                    <span>•</span>
                    <span>{selectedRecord.timestamp.slice(0, 16)}</span>
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedRecord(null)}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Scrollable Body */}
            <div className="p-6 overflow-y-auto space-y-6">
              {/* Top Overview Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Soil Health */}
                <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200 flex flex-col gap-1.5">
                  <div className="flex items-center gap-2 text-emerald-800 font-bold text-xs">
                    <Mountain className="w-4 h-4 text-emerald-600" />
                    <span>Soil Fertility Index</span>
                  </div>
                  <div className="text-2xl font-black text-emerald-900">
                    {selectedRecord.soil_score} <span className="text-xs font-medium text-emerald-700">/ 100</span>
                  </div>
                  <Badge variant={selectedRecord.fertility_class === 'High' ? 'high' : selectedRecord.fertility_class === 'Medium' ? 'medium' : 'low'}>
                    {selectedRecord.fertility_class} Fertility
                  </Badge>
                </div>

                {/* Irrigation */}
                <div className="p-4 rounded-xl bg-sky-50/70 border border-sky-200 flex flex-col gap-1.5">
                  <div className="flex items-center gap-2 text-sky-800 font-bold text-xs">
                    <Droplets className="w-4 h-4 text-sky-600" />
                    <span>Irrigation Demand</span>
                  </div>
                  <div className="text-2xl font-black text-sky-900">
                    {selectedRecord.irrigation_priority}
                  </div>
                  <Badge variant={selectedRecord.irrigation_priority === 'High' ? 'low' : selectedRecord.irrigation_priority === 'Medium' ? 'medium' : 'high'}>
                    Priority Demand
                  </Badge>
                </div>

                {/* AI Confidence */}
                <div className="p-4 rounded-xl bg-purple-50/70 border border-purple-200 flex flex-col gap-1.5">
                  <div className="flex items-center gap-2 text-purple-800 font-bold text-xs">
                    <FlaskConical className="w-4 h-4 text-purple-600" />
                    <span>Model Confidence</span>
                  </div>
                  <div className="text-2xl font-black text-purple-900">
                    {selectedRecord.confidence.toFixed(1)}%
                  </div>
                  <ProgressBar value={selectedRecord.confidence} variant="blue" />
                </div>
              </div>

              {/* Farm Input Parameters Table */}
              {selectedRecord.inputs && Object.keys(selectedRecord.inputs).length > 0 && (
                <div>
                  <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-slate-500" />
                    Recorded Field Parameters
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                    {Object.entries(selectedRecord.inputs).map(([key, val]) => (
                      <div key={key} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-col">
                        <span className="text-[10px] font-bold text-slate-500 uppercase truncate">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-xs font-extrabold text-slate-900 mt-0.5">
                          {val !== null && val !== undefined ? String(val) : '—'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Advisory Summary Notes if present */}
              {selectedRecord.advisory_summary && (
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <h4 className="font-extrabold text-slate-800 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-agri-600" />
                    Agronomic Strategy Summary
                  </h4>
                  <div className="text-slate-600 space-y-1">
                    {selectedRecord.advisory_summary.soil_recommendation && (
                      <p><strong>Soil:</strong> {selectedRecord.advisory_summary.soil_recommendation}</p>
                    )}
                    {selectedRecord.advisory_summary.irrigation_advice && (
                      <p><strong>Irrigation:</strong> {selectedRecord.advisory_summary.irrigation_advice}</p>
                    )}
                    {selectedRecord.advisory_summary.fertilizer_recommendation && (
                      <p><strong>Fertilizer:</strong> {selectedRecord.advisory_summary.fertilizer_recommendation}</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer Actions */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
              <Button
                variant="outline"
                size="md"
                onClick={() => setSelectedRecord(null)}
              >
                Close
              </Button>

              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="md"
                  isLoading={downloadingId === selectedRecord.id}
                  leftIcon={<FileDown className="w-4 h-4" />}
                  onClick={() => handleDownloadPdf(selectedRecord)}
                >
                  Download PDF
                </Button>

                <Button
                  variant="primary"
                  size="md"
                  isLoading={isOpeningResult}
                  rightIcon={<ChevronRight className="w-4 h-4" />}
                  onClick={() => handleInspectInDashboard(selectedRecord)}
                >
                  Open in Result Dashboard
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
