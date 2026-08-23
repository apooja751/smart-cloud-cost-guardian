import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { StatusBadge } from '../components/StatusBadge';
import { Anomaly } from '../types';

export const AnomaliesPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnomalies = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/anomalies${activeAccount ? `?account_id=${activeAccount.id}` : ''}`);
        if (res.data.success) setAnomalies(res.data.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadAnomalies();
  }, [activeAccount]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Cost Surge & Anomaly Detector</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Automated Z-score statistical outlier detection on daily AWS service costs.
        </p>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Date Detected</th>
                <th className="py-3 px-4">AWS Service</th>
                <th className="py-3 px-4 text-right">Expected Cost</th>
                <th className="py-3 px-4 text-right">Actual Cost</th>
                <th className="py-3 px-4 text-right">Surge (%)</th>
                <th className="py-3 px-4 text-center">Severity</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {anomalies.length > 0 ? (
                anomalies.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-900/40">
                    <td className="py-3 px-4 text-slate-300 font-sans">{a.date}</td>
                    <td className="py-3 px-4 font-sans font-bold text-white">{a.service}</td>
                    <td className="py-3 px-4 text-right text-slate-400">${a.expected_cost.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-bold text-rose-400">${a.actual_cost.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-bold text-rose-400">+{a.deviation_percentage.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-center">
                      <StatusBadge status={a.severity} />
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-slate-400 text-xs">{a.status}</span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No cost anomalies detected. Run rate is normal.
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
