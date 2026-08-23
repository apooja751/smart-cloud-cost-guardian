import React, { useState, useEffect } from 'react';
import { DollarSign, BarChart3, TrendingUp, Calendar, Filter } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { DailyCost, ServiceCost } from '../types';

export const CostAnalysisPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [dailyCosts, setDailyCosts] = useState<DailyCost[]>([]);
  const [services, setServices] = useState<ServiceCost[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCosts = async () => {
      setLoading(true);
      try {
        const accParam = activeAccount ? `?account_id=${activeAccount.id}&days=${days}` : `?days=${days}`;
        const [dailyRes, svcRes] = await Promise.all([
          api.get(`/costs/daily${accParam}`),
          api.get(`/costs/services${activeAccount ? `?account_id=${activeAccount.id}` : ''}`)
        ]);
        if (dailyRes.data.success) setDailyCosts(dailyRes.data.data);
        if (svcRes.data.success) setServices(svcRes.data.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadCosts();
  }, [activeAccount, days]);

  const totalCost = dailyCosts.reduce((acc, c) => acc + c.amount, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Cost Analysis & Breakdown</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Historical billing metrics, daily service burn rates, and dimensional cost attribution.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {[14, 30, 60, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                days === d
                  ? 'bg-sky-950 text-sky-400 border border-sky-800'
                  : 'bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {/* Main Bar Chart */}
      <div className="glass-panel rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Daily Cost Distribution</h3>
            <p className="text-xs text-slate-400">Total period spend: ${totalCost.toFixed(2)}</p>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyCosts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="date" stroke="#475569" fontSize={10} />
              <YAxis stroke="#475569" fontSize={10} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                formatter={(v: any) => [`$${Number(v).toFixed(2)}`, 'Cost']}
              />
              <Bar dataKey="amount" fill="#0284c7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Service Table */}
      <div className="glass-panel rounded-2xl p-5 space-y-4 border border-slate-800">
        <h3 className="text-base font-bold text-white">Service Breakdown (Current Month)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">AWS Service</th>
                <th className="py-3 px-4 text-right">Spend ($)</th>
                <th className="py-3 px-4 text-right">% of Total</th>
                <th className="py-3 px-4">Allocation Bar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {services.map((s) => (
                <tr key={s.service} className="hover:bg-slate-900/40">
                  <td className="py-3 px-4 font-sans font-medium text-white">{s.service}</td>
                  <td className="py-3 px-4 text-right font-bold text-slate-200">${s.amount.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right text-sky-400">{s.percentage}%</td>
                  <td className="py-3 px-4">
                    <div className="w-full bg-slate-900 rounded-full h-2">
                      <div className="bg-sky-500 h-2 rounded-full" style={{ width: `${Math.min(100, s.percentage)}%` }}></div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
