import React, { useState, useEffect } from 'react';
import { PieChart, Plus, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { StatusBadge } from '../components/StatusBadge';
import { Budget } from '../types';

export const BudgetsPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [service, setService] = useState('');

  const loadBudgets = async () => {
    try {
      const res = await api.get(`/budgets${activeAccount ? `?account_id=${activeAccount.id}` : ''}`);
      if (res.data.success) setBudgets(res.data.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadBudgets();
  }, [activeAccount]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeAccount) return;
    try {
      await api.post('/budgets', {
        aws_account_id: activeAccount.id,
        name,
        amount: Number(amount),
        currency: 'USD',
        period: 'MONTHLY',
        service: service || null,
        threshold_50: true,
        threshold_75: true,
        threshold_90: true,
        threshold_100: true
      });
      await loadBudgets();
      setShowAdd(false);
      setName('');
      setAmount('');
      setService('');
    } catch (e) {
      alert('Failed to create budget');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/budgets/${id}`);
      await loadBudgets();
    } catch (e) {
      alert('Failed to delete budget');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Budgets & Cost Limits</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Configure threshold alerts (50%, 75%, 90%, 100%) to prevent unexpected month-end bills.
          </p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 text-white text-xs font-bold shadow transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create Budget</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {budgets.map((b) => (
          <div key={b.id} className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-base font-bold text-white">{b.name}</h3>
                <p className="text-xs text-slate-400 font-mono">
                  Target: ${b.amount.toFixed(2)}/{b.period.toLowerCase()} {b.service && `• ${b.service}`}
                </p>
              </div>
              <StatusBadge status={b.status} />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">${b.current_spend.toFixed(2)} spent</span>
                <span className="font-bold text-white">{b.spent_percentage.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-3 relative overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all ${
                    b.spent_percentage >= 100
                      ? 'bg-rose-500'
                      : b.spent_percentage >= 90
                      ? 'bg-amber-500'
                      : 'bg-sky-500'
                  }`}
                  style={{ width: `${Math.min(100, b.spent_percentage)}%` }}
                ></div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
              <span className="text-slate-500 text-[11px]">Alerts: 50% • 75% • 90% • 100%</span>
              <button
                onClick={() => handleDelete(b.id)}
                className="p-1.5 rounded-lg bg-slate-900 text-rose-400 hover:bg-rose-950/40 transition"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md rounded-3xl p-6 shadow-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create FinOps Budget</h3>
              <button onClick={() => setShowAdd(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Budget Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Monthly Production Limit"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Budget Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="2000.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-sky-500 font-mono"
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAdd(false)}
                  className="px-4 py-2 rounded-xl bg-slate-900 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
