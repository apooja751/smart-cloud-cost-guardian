import React, { useState, useEffect } from 'react';
import { FileText, Download, Plus, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { ReportItem } from '../types';

export const ReportsPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [title, setTitle] = useState('Monthly Cloud FinOps & Cost Optimization Audit');
  const [period, setPeriod] = useState('Current Billing Cycle');
  const [generating, setGenerating] = useState(false);

  const loadReports = async () => {
    try {
      const res = await api.get(`/reports${activeAccount ? `?account_id=${activeAccount.id}` : ''}`);
      if (res.data.success) setReports(res.data.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadReports();
  }, [activeAccount]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeAccount) return;
    setGenerating(true);
    try {
      await api.post('/reports/generate', {
        aws_account_id: activeAccount.id,
        title,
        reporting_period: period
      });
      await loadReports();
    } catch (e) {
      alert('Failed to generate PDF report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Executive FinOps Reports</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Downloadable, boardroom-ready PDF reports with KPI tables, service cost breakdowns, and prioritized recommendations.
        </p>
      </div>

      {/* Generator Form */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white">Generate New Executive PDF Report</h3>
        <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2">
            <input
              type="text"
              required
              placeholder="Report Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>
          <button
            type="submit"
            disabled={generating || !activeAccount}
            className="py-2 px-4 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white font-bold text-xs shadow transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <FileText className="w-4 h-4" />
            <span>{generating ? 'Generating PDF...' : 'Generate PDF Report'}</span>
          </button>
        </form>
      </div>

      {/* Generated Reports Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Report Title</th>
                <th className="py-3 px-4">Period</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Generated At</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {reports.length > 0 ? (
                reports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-900/40">
                    <td className="py-3 px-4 font-bold text-white">{r.title}</td>
                    <td className="py-3 px-4 text-slate-300">{r.reporting_period}</td>
                    <td className="py-3 px-4 font-mono text-sky-400 font-bold">{r.format}</td>
                    <td className="py-3 px-4 text-slate-400">{new Date(r.created_at).toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <a
                        href={r.download_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-sky-950 hover:bg-sky-900 text-sky-300 border border-sky-800 font-bold text-xs transition"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download PDF</span>
                      </a>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No reports generated yet. Click Generate above to build your first PDF audit.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
