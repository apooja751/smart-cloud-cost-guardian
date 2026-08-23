import React, { useState, useEffect } from 'react';
import { useParams, NavLink } from 'react-router-dom';
import { ArrowLeft, Server, HardDrive, Database, DollarSign, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import api from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { ResourceDetail } from '../types';

export const ResourceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<ResourceDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDetail = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/resources/${id}`);
        if (res.data.success) {
          setResource(res.data.data);
        }
      } catch (err) {
        console.error('Failed to load resource detail', err);
      } finally {
        setLoading(false);
      }
    };
    loadDetail();
  }, [id]);

  if (loading || !resource) {
    return <div className="py-12 text-center text-slate-400">Loading resource telemetry...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <NavLink
        to="/resources"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Inventory</span>
      </NavLink>

      {/* Header card */}
      <div className="glass-panel rounded-3xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-white">{resource.name || resource.resource_id}</h1>
            <StatusBadge status={resource.state || 'active'} />
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            {resource.resource_id} • {resource.service} • {resource.region}
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400 block uppercase">Est. Monthly Run Rate</span>
          <span className="text-2xl font-extrabold text-emerald-400 font-mono">
            ${resource.estimated_monthly_cost.toFixed(2)}/mo
          </span>
        </div>
      </div>

      {/* Telemetry Chart & Metadata */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Metric History (2 cols) */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-5 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-sky-400" />
            CloudWatch CPU & Utilization Telemetry
          </h3>

          <div className="h-64 w-full">
            {resource.metrics.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={resource.metrics} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="timestamp" stroke="#475569" fontSize={10} tickFormatter={(t) => new Date(t).toLocaleDateString()} />
                  <YAxis stroke="#475569" fontSize={10} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '11px' }}
                    formatter={(val: any) => [`${Number(val).toFixed(1)}%`, 'CPU Avg']}
                  />
                  <Line type="monotone" dataKey="metric_value" stroke="#0284c7" strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No CloudWatch metric points recorded for this resource.
              </div>
            )}
          </div>
        </div>

        {/* Metadata Inspector */}
        <div className="glass-panel rounded-2xl p-5 space-y-4">
          <h3 className="text-base font-bold text-white">AWS Resource Metadata</h3>
          <div className="bg-slate-900/90 rounded-xl p-3 text-xs font-mono border border-slate-800 max-h-64 overflow-y-auto text-sky-300">
            <pre>{JSON.stringify(resource.metadata || {}, null, 2)}</pre>
          </div>
        </div>
      </div>

      {/* Associated Recommendations */}
      <div className="glass-panel rounded-2xl p-5 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          FinOps Cost Optimization Findings for this Resource
        </h3>

        {resource.recommendations.length > 0 ? (
          <div className="space-y-3">
            {resource.recommendations.map((rec) => (
              <div key={rec.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={rec.severity} />
                    <span className="text-xs font-semibold text-slate-400">{rec.category}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white mt-1">{rec.title}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{rec.evidence}</p>
                </div>
                <div className="text-right flex-shrink-0 font-mono">
                  <span className="text-base font-bold text-emerald-400">+${rec.monthly_savings.toFixed(2)}/mo</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">No active waste or optimization recommendations for this resource.</p>
        )}
      </div>
    </div>
  );
};
