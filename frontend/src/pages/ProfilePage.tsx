import React, { useState } from 'react';
import { User as UserIcon, Lock, CheckCircle2, ShieldCheck } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currPassword, setCurrPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [profileMsg, setProfileMsg] = useState<string | null>(null);
  const [passMsg, setPassMsg] = useState<string | null>(null);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg(null);
    try {
      const res = await api.put('/auth/update-profile', { name, email });
      if (res.data.success) {
        updateUser(res.data.data);
        setProfileMsg('Profile updated successfully');
      }
    } catch (e: any) {
      setProfileMsg(e.response?.data?.detail || 'Update failed');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPassMsg(null);
    try {
      const res = await api.post('/auth/change-password', {
        current_password: currPassword,
        new_password: newPassword
      });
      if (res.data.success) {
        setPassMsg('Password changed successfully');
        setCurrPassword('');
        setNewPassword('');
      }
    } catch (e: any) {
      setPassMsg(e.response?.data?.detail || 'Password change failed');
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Account & Profile Settings</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-1">Manage your administrator credentials and profile.</p>
      </div>

      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <UserIcon className="w-4 h-4 text-sky-400" />
          <span>Profile Information</span>
        </h3>
        {profileMsg && <div className="p-2 rounded-lg bg-sky-950 text-sky-300 text-xs">{profileMsg}</div>}
        <form onSubmit={handleUpdateProfile} className="space-y-3 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
            />
          </div>
          <button type="submit" className="px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 font-bold text-white text-xs shadow">
            Save Profile
          </button>
        </form>
      </div>

      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Lock className="w-4 h-4 text-indigo-400" />
          <span>Security & Password</span>
        </h3>
        {passMsg && <div className="p-2 rounded-lg bg-emerald-950 text-emerald-300 text-xs">{passMsg}</div>}
        <form onSubmit={handleChangePassword} className="space-y-3 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Current Password</label>
            <input
              type="password"
              value={currPassword}
              onChange={(e) => setCurrPassword(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-slate-300 font-semibold mb-1">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-white"
            />
          </div>
          <button type="submit" className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-bold text-white text-xs shadow">
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
};
