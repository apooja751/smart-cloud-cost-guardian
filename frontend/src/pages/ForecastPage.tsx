import React, { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, Sparkles, AlertCircle } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { ForecastData } from '../types';

export const ForecastPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadForecast = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/forecast${activeAccount ? `?account_id=${activeAccount.id}` : ''}`);
      if (res.data.success) {
        setForecast(res.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadForecast();
  }, [activeAccount]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Machine Learning Spend Forecast</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            30-day linear trend regression with 95% confidence intervals based on Cost Explorer data.
          </p>
        </div>
        <button
          onClick={loadForecast}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-sky-400 hover:bg-slate-800 transition flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Regenerate Model</span>
        </button>
      </div>

      {forecast && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-panel p-5 rounded-2xl border border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase">Projected Period Spend</span>
              <div className="text-3xl font-extrabold text-indigo-400 font-mono mt-1">
                ${forecast.predicted_total.toFixed(2)}
              </div>
              <span className="text-xs text-slate-500 mt-1 block">Forecast for {forecast.forecast_month}</span>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase">Growth Trend</span>
              <div className={`text-3xl font-extrabold font-mono mt-1 ${forecast.trend_percentage >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {forecast.trend_percentage > 0 ? `+${forecast.trend_percentage}%` : `${forecast.trend_percentage}%`}
              </div>
              <span className="text-xs text-slate-500 mt-1 block">14-day rolling trajectory</span>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase">Model Architecture</span>
              <div className="text-lg font-bold text-white mt-2 truncate">{forecast.model_used}</div>
              <span className="text-xs text-emerald-400 mt-1 block">95% Confidence Interval</span>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-5 space-y-4">
            <h3 className="text-base font-bold text-white">Projected Daily Trajectory with Confidence Bounds</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={forecast.daily_forecasts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="date" stroke="#475569" fontSize={10} tickFormatter={(d) => d.slice(5)} />
                  <YAxis stroke="#475569" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                    formatter={(v: any) => [`$${Number(v).toFixed(2)}`, 'Spend']}
                  />
                  <Area type="monotone" dataKey="upper_bound" stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} strokeDasharray="3 3" />
                  <Area type="monotone" dataKey="predicted_amount" stroke="#38bdf8" strokeWidth={2.5} fill="#38bdf8" fillOpacity={0.2} />
                  <Area type="monotone" dataKey="lower_bound" stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} strokeDasharray="3 3" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
