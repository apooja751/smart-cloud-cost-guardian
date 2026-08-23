import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { Layers, Search, Filter, ArrowUpDown, ChevronRight, Server, Database, HardDrive, Shield } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { StatusBadge } from '../components/StatusBadge';
import { Resource } from '../types';

export const ResourcesPage: React.FC = () => {
  const { activeAccount } = useAWSAccount();
  const [resources, setResources] = useState<Resource[]>([]);
  const [serviceFilter, setServiceFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResources = async () => {
      setLoading(true);
      try {
        let url = `/resources?limit=200`;
        if (activeAccount) url += `&account_id=${activeAccount.id}`;
        if (serviceFilter) url += `&service=${serviceFilter}`;
        if (search) url += `&search=${search}`;

        const res = await api.get(url);
        if (res.data.success) {
          setResources(res.data.data);
        }
      } catch (err) {
        console.error('Failed to load resources', err);
      } finally {
        setLoading(false);
      }
    };
    loadResources();
  }, [activeAccount, serviceFilter, search]);

  const getServiceIcon = (type: string) => {
    switch (type) {
      case 'EC2': return <Server className="w-4 h-4 text-sky-400" />;
      case 'RDS': return <Database className="w-4 h-4 text-indigo-400" />;
      case 'EBS':
      case 'S3':
      case 'Snapshot': return <HardDrive className="w-4 h-4 text-emerald-400" />;
      default: return <Layers className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Resource Inventory</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Multi-service cloud infrastructure discovered via real AWS Boto3 collector APIs.
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[240px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search by resource name or AWS ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={serviceFilter}
            onChange={(e) => setServiceFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="">All Services</option>
            <option value="Amazon EC2">Amazon EC2</option>
            <option value="Amazon EBS">Amazon EBS</option>
            <option value="Amazon RDS">Amazon RDS</option>
            <option value="Amazon S3">Amazon S3</option>
            <option value="Elastic Load Balancing">Elastic Load Balancing</option>
            <option value="AWS Lambda">AWS Lambda</option>
          </select>
        </div>
      </div>

      {/* Resources Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-3.5 px-4">Resource</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Service</th>
                <th className="py-3.5 px-4">Region</th>
                <th className="py-3.5 px-4">State</th>
                <th className="py-3.5 px-4 text-right">Est. Monthly Cost</th>
                <th className="py-3.5 px-4 text-center">Findings</th>
                <th className="py-3.5 px-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium text-slate-300">
              {resources.length > 0 ? (
                resources.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-900/50 transition">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                          {getServiceIcon(r.resource_type)}
                        </div>
                        <div>
                          <p className="font-bold text-white">{r.name || r.resource_id}</p>
                          <p className="text-[11px] text-slate-500 font-mono">{r.resource_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono">{r.resource_type}</td>
                    <td className="py-3 px-4">{r.service}</td>
                    <td className="py-3 px-4 font-mono text-slate-400">{r.region}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={r.state || 'active'} />
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-white">
                      ${r.estimated_monthly_cost.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {r.recommendations_count > 0 ? (
                        <span className="px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 text-[10px] font-bold">
                          {r.recommendations_count} Waste Alert
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[11px]">Optimized</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <NavLink
                        to={`/resources/${r.id}`}
                        className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white inline-flex items-center"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </NavLink>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No resources matched your filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
