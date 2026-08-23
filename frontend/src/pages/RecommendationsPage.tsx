import React, { useState, useEffect } from 'react';
import { Lightbulb, CheckCircle2, XCircle, Clock, DollarSign, Filter, Sparkles } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { StatusBadge } from '../components/StatusBadge';
import { Recommendation } from '../types';

export const RecommendationsPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('Active');
  const [loading, setLoading] = useState(true);

  const loadRecs = async () => {
    setLoading(true);
    try {
      let url = `/recommendations?status=${statusFilter}`;
      if (activeAccount) url += `&account_id=${activeAccount.id}`;
      if (categoryFilter !== 'ALL') url += `&category=${categoryFilter}`;

      const res = await api.get(url);
      if (res.data.success) {
        setRecs(res.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecs();
  }, [activeAccount, categoryFilter, statusFilter]);

  const handleAction = async (id: number, action: 'REVIEW' | 'DISMISS' | 'SNOOZE' | 'ACTIVE') => {
    try {
      await api.post(`/recommendations/${id}/action`, { action });
      await loadRecs();
    } catch (e) {
      alert('Action failed');
    }
  };

  const totalMonthly = recs.filter((r) => r.status === 'Active').reduce((sum, r) => sum + r.estimated_monthly_savings, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">FinOps Cost Optimization Hub</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Deterministic waste detection across Compute, Storage, Database, and Network infrastructure.
          </p>
        </div>
        <div className="glass-panel px-4 py-2 rounded-2xl border border-emerald-800/60 bg-emerald-950/20 text-right">
          <span className="text-[11px] text-slate-400 uppercase font-semibold block">Potential Active Savings</span>
          <span className="text-xl font-extrabold text-emerald-400 font-mono">+${totalMonthly.toFixed(2)}/mo</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 glass-panel p-3 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2 overflow-x-auto">
          {['ALL', 'Compute', 'Storage', 'Database', 'Network'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition whitespace-nowrap ${
                categoryFilter === cat
                  ? 'bg-sky-950 text-sky-400 border border-sky-800'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="Active">Active Opportunities</option>
            <option value="Reviewed">Reviewed</option>
            <option value="Dismissed">Dismissed</option>
            <option value="ALL">All Statuses</option>
          </select>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recs.length > 0 ? (
          recs.map((r) => (
            <div
              key={r.id}
              className="glass-panel rounded-2xl p-5 border border-slate-800 hover:border-slate-700/80 transition space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={r.severity} />
                    <span className="text-xs font-bold text-sky-400 font-mono uppercase">{r.category}</span>
                    <span className="text-xs text-slate-500">• Confidence: {(r.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <h3 className="text-base font-bold text-white">{r.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{r.description}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-xs text-slate-500 block uppercase">Est. Savings</span>
                  <span className="text-xl font-extrabold text-emerald-400 font-mono">
                    +${r.estimated_monthly_savings.toFixed(2)}/mo
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono block">
                    (${r.estimated_annual_savings.toFixed(0)}/yr)
                  </span>
                </div>
              </div>

              {/* Evidence banner */}
              <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800/80 text-xs text-slate-300 font-mono">
                <span className="text-slate-500 font-bold">EVIDENCE: </span>
                {r.evidence}
              </div>

              {/* Action buttons */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
                <span className="text-slate-500 text-[11px]">Advisory only • Review before modifying infrastructure</span>
                <div className="flex items-center gap-2">
                  {r.status === 'Active' ? (
                    <>
                      <button
                        onClick={() => handleAction(r.id, 'REVIEW')}
                        className="px-3 py-1.5 rounded-xl bg-sky-950 hover:bg-sky-900 text-sky-300 border border-sky-800 font-semibold transition"
                      >
                        Mark Reviewed
                      </button>
                      <button
                        onClick={() => handleAction(r.id, 'DISMISS')}
                        className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 font-semibold transition"
                      >
                        Dismiss
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleAction(r.id, 'ACTIVE')}
                      className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-sky-400 border border-slate-700 font-semibold transition"
                    >
                      Re-Activate
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 text-sm">
            No recommendations found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};
