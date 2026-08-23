import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Bell,
  RefreshCw,
  Sparkles,
  ChevronDown,
  Cloud,
  LogOut,
  Shield,
  User as UserIcon,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useAWSAccount } from '../context/AWSAccountContext';
import api from '../services/api';
import { AlertItem } from '../types';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { accounts, activeAccount, setActiveAccount, syncAccount, isDemoMode } = useAWSAccount();
  const [isSyncing, setIsSyncing] = useState(false);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showAlertMenu, setShowAlertMenu] = useState(false);
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/alerts?limit=5');
      if (res.data.success) {
        setAlerts(res.data.data);
        const unread = res.data.data.filter((a: AlertItem) => !a.read).length;
        setUnreadCount(unread);
      }
    } catch (err) {
      console.error('Failed to load alerts', err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    if (!activeAccount || isSyncing) return;
    setIsSyncing(true);
    try {
      await syncAccount(activeAccount.id);
      await fetchAlerts();
    } catch (e) {
      alert('Synchronization error. Check account credentials.');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.post('/alerts/read-all');
      setUnreadCount(0);
      fetchAlerts();
    } catch (e) {}
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Account Selector */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <button
            onClick={() => setShowAccountMenu(!showAccountMenu)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-sm text-slate-200 transition"
          >
            <Cloud className="w-4 h-4 text-sky-400" />
            <span className="font-semibold text-white max-w-[200px] truncate">
              {activeAccount ? activeAccount.account_name : 'Select Account'}
            </span>
            {activeAccount && (
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                {activeAccount.account_id}
              </span>
            )}
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showAccountMenu && (
            <div className="absolute left-0 mt-2 w-72 glass-panel rounded-2xl shadow-2xl p-2 z-50 border border-slate-700 animate-scale-up">
              <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                Connected AWS Accounts
              </div>
              <div className="max-h-60 overflow-y-auto py-1 space-y-1">
                {accounts.map((acc) => (
                  <button
                    key={acc.id}
                    onClick={() => {
                      setActiveAccount(acc);
                      setShowAccountMenu(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left text-xs transition ${
                      activeAccount?.id === acc.id
                        ? 'bg-sky-950/80 text-sky-300 border border-sky-800'
                        : 'text-slate-300 hover:bg-slate-800/80'
                    }`}
                  >
                    <div>
                      <p className="font-bold truncate">{acc.account_name}</p>
                      <p className="text-[11px] text-slate-400 font-mono">{acc.account_id} ({acc.region})</p>
                    </div>
                    {acc.connection_type === 'DEMO' && (
                      <span className="text-[10px] bg-indigo-950 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-800">
                        DEMO
                      </span>
                    )}
                  </button>
                ))}
              </div>
              <div className="pt-2 border-t border-slate-800">
                <NavLink
                  to="/accounts"
                  onClick={() => setShowAccountMenu(false)}
                  className="block text-center text-xs font-bold text-sky-400 hover:text-sky-300 py-1"
                >
                  + Connect New AWS Account
                </NavLink>
              </div>
            </div>
          )}
        </div>

        {/* Sync Now button */}
        <button
          onClick={handleSync}
          disabled={isSyncing || !activeAccount}
          title="Synchronize real AWS APIs now"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-slate-300 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-sky-400 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>{isSyncing ? 'Syncing...' : 'Sync AWS'}</span>
        </button>

        {isDemoMode && (
          <span className="hidden md:inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-950/80 text-indigo-300 border border-indigo-800/80 animate-pulse">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            [DEMO DATA ENVIRONMENT]
          </span>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Notifications Bell */}
        <div className="relative">
          <button
            onClick={() => setShowAlertMenu(!showAlertMenu)}
            className="relative p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center animate-bounce">
                {unreadCount}
              </span>
            )}
          </button>

          {showAlertMenu && (
            <div className="absolute right-0 mt-2 w-80 glass-panel rounded-2xl shadow-2xl p-3 z-50 border border-slate-700 animate-scale-up">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-bold text-white uppercase tracking-wider">Alerts & Waste</span>
                {unreadCount > 0 && (
                  <button onClick={handleMarkAllRead} className="text-[11px] text-sky-400 hover:underline">
                    Mark all read
                  </button>
                )}
              </div>
              <div className="py-2 space-y-2 max-h-64 overflow-y-auto">
                {alerts.length > 0 ? (
                  alerts.map((a) => (
                    <div key={a.id} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                      <div className="flex items-start justify-between gap-1">
                        <span className="font-bold text-slate-200">{a.title}</span>
                        <span className="text-[10px] text-slate-500">{new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                      <p className="text-slate-400 mt-1 text-[11px] leading-snug">{a.message}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-xs text-slate-500 py-4">No active alerts</p>
                )}
              </div>
              <NavLink
                to="/alerts"
                onClick={() => setShowAlertMenu(false)}
                className="block text-center text-xs font-bold text-sky-400 hover:text-sky-300 pt-2 border-t border-slate-800"
              >
                View all notifications →
              </NavLink>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition"
          >
            <UserIcon className="w-4 h-4 text-sky-400" />
            <span>{user?.name || 'Account'}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 glass-panel rounded-2xl shadow-2xl p-2 z-50 border border-slate-700 animate-scale-up">
              <div className="px-3 py-2 text-xs border-b border-slate-800">
                <p className="font-bold text-white">{user?.name}</p>
                <p className="text-slate-400 text-[11px]">{user?.email}</p>
                <span className="inline-block mt-1 text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-sky-400">
                  {user?.role}
                </span>
              </div>
              <div className="py-1">
                <NavLink
                  to="/profile"
                  onClick={() => setShowUserMenu(false)}
                  className="block px-3 py-1.5 rounded-lg text-xs text-slate-300 hover:bg-slate-800"
                >
                  Profile & Settings
                </NavLink>
                {user?.role === 'ADMIN' && (
                  <NavLink
                    to="/admin"
                    onClick={() => setShowUserMenu(false)}
                    className="block px-3 py-1.5 rounded-lg text-xs text-slate-300 hover:bg-slate-800"
                  >
                    Admin Portal
                  </NavLink>
                )}
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    logout();
                  }}
                  className="w-full text-left flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-rose-400 hover:bg-rose-950/40 mt-1"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
