import React, { useState, useEffect } from 'react';
import { ShieldCheck, Users, Activity, HardDrive, Clock } from 'lucide-react';
import api from '../services/api';

export const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAdmin = async () => {
      setLoading(true);
      try {
        const [usersRes, logsRes, healthRes] = await Promise.all([
          api.get('/admin/users'),
          api.get('/admin/audit-logs?limit=50'),
          api.get('/admin/system-health')
        ]);
        if (usersRes.data.success) setUsers(usersRes.data.data);
        if (logsRes.data.success) setLogs(logsRes.data.data);
        if (healthRes.data.success) setHealth(healthRes.data.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadAdmin();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">System Administration</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Platform health metrics, registered users, and system audit trail.
        </p>
      </div>

      {health && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase">System Status</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1 font-mono">{health.status}</div>
          </div>
          <div className="glass-panel p-4 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase">Active Users</span>
            <div className="text-2xl font-extrabold text-white mt-1 font-mono">{health.active_users}</div>
          </div>
          <div className="glass-panel p-4 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase">Connected AWS Accounts</span>
            <div className="text-2xl font-extrabold text-sky-400 mt-1 font-mono">{health.connected_accounts}</div>
          </div>
          <div className="glass-panel p-4 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase">Tracked Resources</span>
            <div className="text-2xl font-extrabold text-indigo-400 mt-1 font-mono">{health.total_resources}</div>
          </div>
        </div>
      )}

      {/* Audit Logs Table */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white">Live System Audit Logs</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Resource Target</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-900/40">
                  <td className="py-3 px-4 text-slate-400 font-sans">{new Date(l.created_at).toLocaleString()}</td>
                  <td className="py-3 px-4 text-slate-300">{l.user_email || 'System'}</td>
                  <td className="py-3 px-4 font-bold text-sky-400">{l.action}</td>
                  <td className="py-3 px-4 text-slate-400">{l.resource_id || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
