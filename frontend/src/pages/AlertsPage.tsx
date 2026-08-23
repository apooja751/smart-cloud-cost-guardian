import React, { useState, useEffect } from 'react';
import { Bell, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import api from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { AlertItem } from '../types';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.get('/alerts?limit=100');
      if (res.data.success) setAlerts(res.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleMarkRead = async (id: number) => {
    try {
      await api.post(`/alerts/${id}/read`);
      await loadAlerts();
    } catch (e) {}
  };

  const handleMarkAll = async () => {
    try {
      await api.post('/alerts/read-all');
      await loadAlerts();
    } catch (e) {}
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Alerts & Waste Notifications</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Real-time notifications triggered by budget thresholds, cost spikes, and idle resource detectors.
          </p>
        </div>
        <button
          onClick={handleMarkAll}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-sky-400 hover:bg-slate-800 transition"
        >
          Mark All as Read
        </button>
      </div>

      <div className="space-y-3">
        {alerts.length > 0 ? (
          alerts.map((a) => (
            <div
              key={a.id}
              className={`glass-panel rounded-2xl p-4 border transition flex items-center justify-between gap-4 ${
                a.read ? 'border-slate-800/80 opacity-75' : 'border-sky-500/50 bg-sky-950/10'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <StatusBadge status={a.severity} />
                  <span className="text-xs font-bold text-white">{a.title}</span>
                  <span className="text-[10px] text-slate-500">{new Date(a.created_at).toLocaleString()}</span>
                </div>
                <p className="text-xs text-slate-300">{a.message}</p>
              </div>

              {!a.read && (
                <button
                  onClick={() => handleMarkRead(a.id)}
                  className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs text-sky-400 font-semibold border border-slate-700 flex-shrink-0"
                >
                  Mark Read
                </button>
              )}
            </div>
          ))
        ) : (
          <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 text-sm">
            No alerts found.
          </div>
        )}
      </div>
    </div>
  );
};
