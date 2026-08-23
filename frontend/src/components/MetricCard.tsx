import React from 'react';
import { ArrowUpRight, ArrowDownRight, HelpCircle } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    label: string;
    isPositiveGood?: boolean;
  };
  icon: React.ReactNode;
  tooltip?: string;
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  tooltip,
  highlight = false,
}) => {
  return (
    <div
      className={`glass-panel glass-panel-hover rounded-2xl p-5 relative overflow-hidden transition-all duration-200 ${
        highlight ? 'border-sky-500/40 bg-sky-950/10' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {title}
            {tooltip && (
              <span title={tooltip} className="cursor-help text-slate-500 hover:text-slate-300">
                <HelpCircle className="w-3.5 h-3.5" />
              </span>
            )}
          </div>
          <div className="mt-2 text-2xl font-extrabold tracking-tight text-white font-mono">{value}</div>
          {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
        </div>
        <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-sky-400 shadow-inner">
          {icon}
        </div>
      </div>

      {trend && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          {trend.value >= 0 ? (
            <span className={`flex items-center font-semibold ${trend.isPositiveGood ? 'text-emerald-400' : 'text-rose-400'}`}>
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
              {Math.abs(trend.value)}%
            </span>
          ) : (
            <span className={`flex items-center font-semibold ${trend.isPositiveGood ? 'text-rose-400' : 'text-emerald-400'}`}>
              <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
              {Math.abs(trend.value)}%
            </span>
          )}
          <span className="text-slate-500">{trend.label}</span>
        </div>
      )}
    </div>
  );
};
