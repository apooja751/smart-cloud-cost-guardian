import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  DollarSign,
  TrendingDown,
  TrendingUp,
  Layers,
  Sparkles,
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { MetricCard } from '../components/MetricCard';
import { HealthGauge } from '../components/HealthGauge';
import { StatusBadge } from '../components/StatusBadge';
import { CostSummary, DailyCost, ServiceCost, Recommendation, HealthScore } from '../types';

const COLORS = ['#0284c7', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#64748b'];

export const DashboardPage: React.FC = () => {
  const { activeAccount, isDemoMode } = useAWSAccount();
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [dailyCosts, setDailyCosts] = useState<DailyCost[]>([]);
  const [serviceCosts, setServiceCosts] = useState<ServiceCost[]>([]);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [health, setHealth] = useState<HealthScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      try {
        const accParam = activeAccount ? `?account_id=${activeAccount.id}` : '';
        const [sumRes, dailyRes, svcRes, recsRes, healthRes] = await Promise.all([
          api.get(`/costs/summary${accParam}`),
          api.get(`/costs/daily${accParam}&days=30`),
          api.get(`/costs/services${accParam}`),
          api.get(`/recommendations${accParam}`),
          api.get(`/health-score${accParam}`)
        ]);

        if (sumRes.data.success) setSummary(sumRes.data.data);
        if (dailyRes.data.success) setDailyCosts(dailyRes.data.data);
        if (svcRes.data.success) setServiceCosts(svcRes.data.data);
        if (recsRes.data.success) setRecs(recsRes.data.data.slice(0, 4));
        if (healthRes.data.success) setHealth(healthRes.data.data);
      } catch (err) {
        console.error('Failed to load dashboard', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [activeAccount]);

  return (
    <div className="space-y-6">
      {/* Top Banner / Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">FinOps Executive Overview</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Real-time AWS resource utilization, spend projections, and automated savings intelligence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <NavLink
            to="/assistant"
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 transition flex items-center gap-1.5"
          >
            <Sparkles className="w-4 h-4 text-sky-200" />
            <span>Ask AI FinOps Copilot</span>
          </NavLink>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Current Month Spend"
          value={`$${(summary?.current_month_cost || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtitle="Actual recorded billing to date"
          trend={{
            value: summary?.cost_change_percentage || 0,
            label: 'vs previous month',
            isPositiveGood: false
          }}
          icon={<DollarSign className="w-5 h-5 text-sky-400" />}
          highlight
        />

        <MetricCard
          title="Potential Monthly Savings"
          value={`$${(summary?.potential_monthly_savings || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtitle={`$${((summary?.potential_monthly_savings || 0) * 12).toLocaleString('en-US', { minimumFractionDigits: 0 })}/year identified`}
          icon={<TrendingDown className="w-5 h-5 text-emerald-400" />}
          tooltip="Calculated from 8+ deterministic FinOps waste rules"
        />

        <MetricCard
          title="Forecasted Month-End"
          value={`$${(summary?.forecasted_monthly_cost || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtitle="ML Linear Trend projection"
          icon={<TrendingUp className="w-5 h-5 text-indigo-400" />}
        />

        <MetricCard
          title="Active Opportunities"
          value={recs.length}
          subtitle="Optimization actions ready"
          icon={<Lightbulb className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Spend Trend (2 cols) */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Daily Cost Trend (Last 30 Days)</h3>
              <p className="text-xs text-slate-400">Daily AWS cost distribution from Cost Explorer / Boto3</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-slate-900 text-slate-400 border border-slate-800">
              USD ($)
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyCosts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284c7" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#475569" fontSize={10} tickLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Cost']}
                />
                <Area type="monotone" dataKey="amount" stroke="#0284c7" strokeWidth={2.5} fillOpacity={1} fill="url(#costGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cloud Health Score Radial & Breakdown */}
        <div className="glass-panel rounded-2xl p-5 space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Cloud Health Score</h3>
            <NavLink to="/recommendations" className="text-xs text-sky-400 hover:underline">
              Improve Score →
            </NavLink>
          </div>

          <div className="flex items-center justify-center py-2">
            <HealthGauge score={health?.overall_score || 80} grade={health?.grade || 'B'} size={140} />
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between text-slate-400">
              <span>Cost Efficiency</span>
              <span className="font-mono text-white font-bold">{health?.breakdown?.cost_efficiency || 25}/30</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5">
              <div className="bg-sky-500 h-1.5 rounded-full" style={{ width: `${((health?.breakdown?.cost_efficiency || 25) / 30) * 100}%` }}></div>
            </div>

            <div className="flex items-center justify-between text-slate-400">
              <span>Resource Utilization</span>
              <span className="font-mono text-white font-bold">{health?.breakdown?.resource_utilization || 22}/25</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5">
              <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${((health?.breakdown?.resource_utilization || 22) / 25) * 100}%` }}></div>
            </div>

            <div className="flex items-center justify-between text-slate-400">
              <span>Waste Cleanliness</span>
              <span className="font-mono text-white font-bold">{health?.breakdown?.optimization_opportunities || 18}/20</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5">
              <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${((health?.breakdown?.optimization_opportunities || 18) / 20) * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Service Spend Donut & Top Recommendations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Service Donut Chart */}
        <div className="glass-panel rounded-2xl p-5 space-y-4">
          <h3 className="text-base font-bold text-white">Spend by AWS Service</h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={serviceCosts}
                  dataKey="amount"
                  nameKey="service"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {serviceCosts.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                  formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Spend']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 text-xs">
            {serviceCosts.slice(0, 4).map((s, idx) => (
              <div key={s.service} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                  <span className="text-slate-300 truncate max-w-[150px]">{s.service}</span>
                </div>
                <span className="font-mono text-white font-semibold">${s.amount.toFixed(2)} ({s.percentage}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Optimization Opportunities (2 cols) */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Top FinOps Cost Optimization Opportunities</h3>
              <p className="text-xs text-slate-400">High-confidence recommendations prioritized by monthly savings</p>
            </div>
            <NavLink to="/recommendations" className="text-xs font-semibold text-sky-400 hover:underline">
              View All ({recs.length}) →
            </NavLink>
          </div>

          <div className="space-y-3">
            {recs.length > 0 ? (
              recs.map((r) => (
                <div
                  key={r.id}
                  className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <StatusBadge status={r.severity} />
                      <span className="text-xs font-semibold text-slate-400">{r.category}</span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{r.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-1">{r.evidence}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-base font-mono font-extrabold text-emerald-400">
                      +${r.estimated_monthly_savings.toFixed(2)}/mo
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      ${r.estimated_annual_savings.toFixed(0)}/yr
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500 text-xs">
                No active recommendations. Infrastructure is running optimally!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
