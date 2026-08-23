import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cloud,
  Layers,
  DollarSign,
  Lightbulb,
  TrendingUp,
  AlertTriangle,
  PieChart,
  Bell,
  Sparkles,
  FileText,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
  { name: 'AWS Accounts', path: '/accounts', icon: <Cloud className="w-5 h-5" /> },
  { name: 'Resource Inventory', path: '/resources', icon: <Layers className="w-5 h-5" /> },
  { name: 'Cost Analysis', path: '/costs', icon: <DollarSign className="w-5 h-5" /> },
  { name: 'Recommendations', path: '/recommendations', icon: <Lightbulb className="w-5 h-5" /> },
  { name: 'Forecast & ML', path: '/forecast', icon: <TrendingUp className="w-5 h-5" /> },
  { name: 'Cost Anomalies', path: '/anomalies', icon: <AlertTriangle className="w-5 h-5" /> },
  { name: 'Budgets & Limits', path: '/budgets', icon: <PieChart className="w-5 h-5" /> },
  { name: 'Alerts Center', path: '/alerts', icon: <Bell className="w-5 h-5" /> },
  { name: 'AI FinOps Copilot', path: '/assistant', icon: <Sparkles className="w-5 h-5 text-indigo-400" /> },
  { name: 'Executive Reports', path: '/reports', icon: <FileText className="w-5 h-5" /> },
  { name: 'Admin Portal', path: '/admin', icon: <ShieldCheck className="w-5 h-5" />, adminOnly: true },
];

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-800/80 bg-slate-950/90 flex flex-col justify-between p-4 min-h-screen">
      <div>
        {/* Brand */}
        <div className="flex items-center gap-3 px-3 py-4 mb-4 border-b border-slate-800/60">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white tracking-tight leading-none">SCCG</h1>
            <p className="text-[10px] text-sky-400 font-semibold tracking-wider uppercase mt-1">FinOps Guardian</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            if (item.adminOnly && user?.role !== 'ADMIN') return null;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-950/60 text-sky-400 border border-sky-800/60 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`
                }
              >
                {item.icon}
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User profile footer */}
      <div className="pt-4 border-t border-slate-800/80">
        <NavLink
          to="/profile"
          className="flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-slate-900/80 transition"
        >
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-sky-400">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="overflow-hidden">
            <p className="font-semibold text-white truncate">{user?.name || 'FinOps User'}</p>
            <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
          </div>
        </NavLink>
      </div>
    </aside>
  );
};
