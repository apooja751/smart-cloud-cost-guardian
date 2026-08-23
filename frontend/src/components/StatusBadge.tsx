import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'severity' | 'state' | 'status' | 'grade';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'status' }) => {
  const s = status.toUpperCase();

  let colors = 'bg-slate-800 text-slate-300 border-slate-700';

  if (s === 'CRITICAL' || s === 'EXCEEDED' || s === 'ERROR' || s === 'F') {
    colors = 'bg-rose-950/60 text-rose-300 border-rose-800/60';
  } else if (s === 'HIGH' || s === 'WARNING' || s === 'D') {
    colors = 'bg-amber-950/60 text-amber-300 border-amber-800/60';
  } else if (s === 'MEDIUM' || s === 'REVIEWED' || s === 'C') {
    colors = 'bg-sky-950/60 text-sky-300 border-sky-800/60';
  } else if (s === 'LOW' || s === 'OK' || s === 'CONNECTED' || s === 'RUNNING' || s === 'ACTIVE' || s === 'A' || s === 'B') {
    colors = 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60';
  } else if (s === 'DISMISSED' || s === 'STOPPED' || s === 'SNOOZED') {
    colors = 'bg-slate-900 text-slate-400 border-slate-700';
  } else if (s === 'SYNCHRONIZING') {
    colors = 'bg-indigo-950/60 text-indigo-300 border-indigo-800/60 animate-pulse';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colors}`}>
      {status}
    </span>
  );
};
