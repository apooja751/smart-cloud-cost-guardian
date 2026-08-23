import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldCheck,
  Zap,
  TrendingDown,
  BrainCircuit,
  Lock,
  ArrowRight,
  Server,
  Database,
  HardDrive,
  BarChart3,
  Cpu,
  Sparkles
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-sky-500 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md px-8 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-lg font-extrabold text-white tracking-tight">Smart Cloud Cost Guardian</span>
            <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
              FinOps AI v1.0
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <NavLink
            to="/login"
            className="text-sm font-semibold text-slate-300 hover:text-white px-4 py-2 rounded-xl transition"
          >
            Sign In
          </NavLink>
          <NavLink
            to="/register"
            className="text-sm font-bold text-white bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 px-5 py-2.5 rounded-xl shadow-lg shadow-sky-500/20 transition flex items-center gap-1.5"
          >
            <span>Launch Platform</span>
            <ArrowRight className="w-4 h-4" />
          </NavLink>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-6 py-20 md:py-28 max-w-6xl mx-auto text-center space-y-8 relative">
        <div className="absolute inset-0 -z-10 flex items-center justify-center">
          <div className="w-[600px] h-[350px] bg-gradient-to-tr from-sky-600/20 to-indigo-600/20 rounded-full blur-3xl"></div>
        </div>

        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-sky-400 shadow-inner">
          <Sparkles className="w-4 h-4 text-sky-400" />
          Production-Grade AI Cloud Cost Optimization & FinOps Intelligence
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Eliminate Cloud Waste. <br />
          <span className="bg-gradient-to-r from-sky-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">
            Automate FinOps with Factual AI.
          </span>
        </h1>

        <p className="text-base md:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
          Connect your AWS environment securely with least-privilege IAM roles. Instantly detect idle EC2 instances, unattached EBS volumes, unindexed RDS databases, forecast month-end spend with Scikit-learn ML, and query your cloud costs with our zero-hallucination AI copilot.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <NavLink
            to="/login"
            className="px-8 py-4 rounded-2xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold text-base shadow-xl shadow-sky-600/25 transition flex items-center gap-2"
          >
            <span>Explore Live Demo Account</span>
            <ArrowRight className="w-5 h-5" />
          </NavLink>
          <NavLink
            to="/register"
            className="px-8 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-bold text-base transition"
          >
            Connect AWS Account
          </NavLink>
        </div>

        {/* Live Metrics Showcase */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-12 text-left">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase">Average Waste Identified</div>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-1">28.4%</div>
            <div className="text-xs text-slate-500 mt-1">Immediate monthly savings</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase">Detection Rules</div>
            <div className="text-3xl font-extrabold text-sky-400 font-mono mt-1">8+ FinOps</div>
            <div className="text-xs text-slate-500 mt-1">Deterministic evaluators</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase">Forecasting Accuracy</div>
            <div className="text-3xl font-extrabold text-indigo-400 font-mono mt-1">95% CI</div>
            <div className="text-xs text-slate-500 mt-1">Linear trend + moving avg</div>
          </div>
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="text-xs font-semibold text-slate-400 uppercase">Security Posture</div>
            <div className="text-3xl font-extrabold text-white font-mono mt-1">Read-Only</div>
            <div className="text-xs text-slate-500 mt-1">Advisory-only execution</div>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="px-6 py-16 bg-slate-900/40 border-t border-slate-800">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <h2 className="text-3xl font-bold text-white tracking-tight">Full-Stack Cloud Intelligence Capabilities</h2>
            <p className="text-sm text-slate-400">Everything enterprise FinOps and engineering teams need to control cloud spend.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-sky-950 text-sky-400 flex items-center justify-center border border-sky-800">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Deterministic FinOps Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Rules-based evaluation for Idle EC2, Stopped Instances, Unattached EBS Volumes, 60d+ Snapshots, Unused Elastic IPs, Low-traffic Load Balancers, and Underutilized RDS.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-950 text-indigo-400 flex items-center justify-center border border-indigo-800">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Grounded AI FinOps Copilot</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Zero-hallucination assistant directly querying live AWS metrics, Cost Explorer history, anomalies, and active recommendations with clear audit evidence.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950 text-emerald-400 flex items-center justify-center border border-emerald-800">
                <BarChart3 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Explainable Cloud Health Score</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                0–100 weighted index evaluating Cost Efficiency, Resource Utilization, Recommendation Adoption, Budget Adherence, and Anomaly Cleanliness.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 px-8 py-6 text-center text-xs text-slate-500">
        <p>© 2026 Smart Cloud Cost Guardian (SCCG). AI-Powered Cloud Cost Optimization & FinOps Platform.</p>
      </footer>
    </div>
  );
};
