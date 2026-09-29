import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { ShieldCheck, Mail, Lock, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (role: 'user' | 'admin') => {
    setError(null);
    if (role === 'admin') {
      setEmail('admin@sccg.io');
      setPassword('Admin123!Secure');
    } else {
      setEmail('demo@sccg.io');
      setPassword('Demo123!Secure');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative">
      <div className="absolute inset-0 -z-10 flex items-center justify-center">
        <div className="w-[500px] h-[300px] bg-sky-600/15 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-md glass-panel rounded-3xl p-8 border border-slate-800 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center mx-auto shadow-lg shadow-sky-500/20">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Welcome Back</h2>
          <p className="text-xs text-slate-400">Sign in to your FinOps Resource Intelligence portal</p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-sky-600/20 transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Fill Buttons */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <p className="text-[11px] font-semibold text-slate-400 text-center uppercase tracking-wider">
            One-Click Quick Test Credentials
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleDemoFill('user')}
              className="px-3 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-sky-500 text-xs font-semibold text-sky-400 flex items-center justify-center gap-1.5 transition cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-sky-400" />
              <span>Demo User</span>
            </button>
            <button
              type="button"
              onClick={() => handleDemoFill('admin')}
              className="px-3 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-indigo-500 text-xs font-semibold text-indigo-400 flex items-center justify-center gap-1.5 transition cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Admin User</span>
            </button>
          </div>
        </div>

        <div className="text-center text-xs text-slate-400">
          Don't have an account?{' '}
          <NavLink to="/register" className="text-sky-400 font-bold hover:underline">
            Register now
          </NavLink>
        </div>
      </div>
    </div>
  );
};
