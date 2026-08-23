import React, { useState } from 'react';
import { Cloud, Plus, RefreshCw, Trash2, CheckCircle2, ShieldCheck, Key, Sparkles, ExternalLink } from 'lucide-react';
import api from '../services/api';
import { useAWSAccount } from '../context/AWSAccountContext';
import { StatusBadge } from '../components/StatusBadge';
import { ConfirmModal } from '../components/ConfirmModal';

export const AWSAccountsPage: React.FC = () => {
  const { accounts, refreshAccounts, activeAccount, setActiveAccount, syncAccount } = useAWSAccount();
  const [showAddModal, setShowAddModal] = useState(false);
  const [connType, setConnType] = useState<'IAM_ROLE' | 'ACCESS_KEY' | 'DEMO'>('IAM_ROLE');
  const [accountName, setAccountName] = useState('');
  const [accountId, setAccountId] = useState('');
  const [region, setRegion] = useState('us-east-1');
  const [roleArn, setRoleArn] = useState('');
  const [externalId, setExternalId] = useState('');
  const [accessKey, setAccessKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState<number | null>(null);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.post('/aws/test-connection', {
        connection_type: connType,
        region,
        role_arn: roleArn,
        external_id: externalId,
        aws_access_key_id: accessKey,
        aws_secret_access_key: secretKey,
        demo_mode: connType === 'DEMO'
      });
      if (res.data.success) {
        setTestResult({ success: res.data.data.is_valid, message: res.data.data.message });
      }
    } catch (e: any) {
      setTestResult({ success: false, message: e.response?.data?.detail || 'Connection test failed' });
    } finally {
      setTesting(false);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setConnecting(true);
    try {
      const targetAccId = connType === 'DEMO' ? '123456789012' : accountId;
      const targetName = connType === 'DEMO' ? (accountName || 'Demo Production AWS') : accountName;

      await api.post('/aws/connect', {
        account_name: targetName,
        account_id: targetAccId,
        region,
        connection_type: connType,
        role_arn: roleArn,
        external_id: externalId,
        aws_access_key_id: accessKey,
        aws_secret_access_key: secretKey
      });
      await refreshAccounts();
      setShowAddModal(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to connect AWS Account');
    } finally {
      setConnecting(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!accountToDelete) return;
    try {
      await api.delete(`/aws/accounts/${accountToDelete}`);
      await refreshAccounts();
      setAccountToDelete(null);
    } catch (e) {
      alert('Failed to disconnect account');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">AWS Account Integrations</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Connect live AWS accounts using secure cross-account STS IAM AssumeRole or explore instant demo mode.
          </p>
        </div>
        <button
          onClick={() => {
            setTestResult(null);
            setShowAddModal(true);
          }}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-sm font-bold shadow-lg shadow-sky-500/20 transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>Connect AWS Account</span>
        </button>
      </div>

      {/* Account Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {accounts.map((acc) => (
          <div
            key={acc.id}
            className={`glass-panel rounded-2xl p-5 space-y-4 border transition ${
              activeAccount?.id === acc.id ? 'border-sky-500/60 shadow-lg shadow-sky-950/40' : 'border-slate-800'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sky-400">
                  <Cloud className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">{acc.account_name}</h3>
                  <p className="text-xs text-slate-400 font-mono">{acc.account_id} • {acc.region}</p>
                </div>
              </div>
              <StatusBadge status={acc.status} />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs py-2 border-y border-slate-800/60 font-mono">
              <div>
                <span className="text-slate-500 text-[11px] block">Auth Type</span>
                <span className="text-slate-200 font-bold">{acc.connection_type}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">Resources</span>
                <span className="text-sky-400 font-bold">{acc.discovered_resources_count} tracked</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <button
                onClick={() => setActiveAccount(acc)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                  activeAccount?.id === acc.id
                    ? 'bg-sky-950 text-sky-300 border border-sky-800'
                    : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-700'
                }`}
              >
                {activeAccount?.id === acc.id ? 'Active Focus' : 'Set as Focus'}
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => syncAccount(acc.id)}
                  title="Synchronize APIs"
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setAccountToDelete(acc.id)}
                  title="Disconnect Account"
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-rose-400 hover:bg-rose-950/40 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Connect Account Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-lg rounded-3xl p-6 shadow-2xl border border-slate-800 space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Connect AWS Account</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            {/* Connection Type Tabs */}
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setConnType('IAM_ROLE')}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
                  connType === 'IAM_ROLE'
                    ? 'bg-sky-950 text-sky-400 border border-sky-800'
                    : 'bg-slate-900 text-slate-400 border border-slate-800'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>IAM Role (Recommended)</span>
              </button>
              <button
                type="button"
                onClick={() => setConnType('ACCESS_KEY')}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
                  connType === 'ACCESS_KEY'
                    ? 'bg-sky-950 text-sky-400 border border-sky-800'
                    : 'bg-slate-900 text-slate-400 border border-slate-800'
                }`}
              >
                <Key className="w-3.5 h-3.5" />
                <span>Access Keys</span>
              </button>
              <button
                type="button"
                onClick={() => setConnType('DEMO')}
                className={`py-2 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
                  connType === 'DEMO'
                    ? 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                    : 'bg-slate-900 text-slate-400 border border-slate-800'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Demo Mode</span>
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-4">
              {connType !== 'DEMO' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Account Display Name</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Production Main AWS"
                      value={accountName}
                      onChange={(e) => setAccountName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">12-Digit Account ID</label>
                      <input
                        type="text"
                        required
                        placeholder="123456789012"
                        value={accountId}
                        onChange={(e) => setAccountId(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Primary Region</label>
                      <select
                        value={region}
                        onChange={(e) => setRegion(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                      >
                        <option value="us-east-1">us-east-1 (N. Virginia)</option>
                        <option value="us-west-2">us-west-2 (Oregon)</option>
                        <option value="eu-west-1">eu-west-1 (Ireland)</option>
                        <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
                      </select>
                    </div>
                  </div>

                  {connType === 'IAM_ROLE' ? (
                    <>
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">Cross-Account Role ARN</label>
                        <input
                          type="text"
                          required
                          placeholder="arn:aws:iam::123456789012:role/SmartCloudCostGuardianRole"
                          value={roleArn}
                          onChange={(e) => setRoleArn(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">External ID (Optional)</label>
                        <input
                          type="text"
                          placeholder="sccg-audit-secure-token"
                          value={externalId}
                          onChange={(e) => setExternalId(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">AWS Access Key ID</label>
                        <input
                          type="text"
                          required
                          placeholder="AKIAIOSFODNN7EXAMPLE"
                          value={accessKey}
                          onChange={(e) => setAccessKey(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">AWS Secret Access Key</label>
                        <input
                          type="password"
                          required
                          placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                          value={secretKey}
                          onChange={(e) => setSecretKey(e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
                        />
                      </div>
                    </>
                  )}
                </>
              )}

              {connType === 'DEMO' && (
                <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-800/60 space-y-2 text-xs text-slate-300">
                  <p className="font-bold text-indigo-300">🌟 Zero-Setup Simulated AWS Account</p>
                  <p>
                    Instantly loads 20+ realistic cloud resources (EC2, EBS, RDS, S3, Lambda, ELB), 60 days of historical Cost Explorer billing data, intentional anomaly spikes, and 11 actionable recommendations.
                  </p>
                </div>
              )}

              {testResult && (
                <div
                  className={`p-3 rounded-xl text-xs border ${
                    testResult.success
                      ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800'
                      : 'bg-rose-950/60 text-rose-300 border-rose-800'
                  }`}
                >
                  {testResult.message}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                {connType !== 'DEMO' && (
                  <button
                    type="button"
                    onClick={handleTestConnection}
                    disabled={testing}
                    className="px-4 py-2 text-xs font-semibold text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl transition"
                  >
                    {testing ? 'Testing...' : 'Test Connection'}
                  </button>
                )}
                <button
                  type="submit"
                  disabled={connecting}
                  className="px-5 py-2 text-xs font-bold text-white bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 rounded-xl shadow transition"
                >
                  {connecting ? 'Connecting...' : 'Save & Synchronize'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={!!accountToDelete}
        title="Disconnect AWS Account"
        message="Are you sure you want to disconnect this AWS account? All local cached resources and metric snapshots will be removed."
        confirmText="Disconnect Account"
        isDestructive
        onConfirm={handleDeleteAccount}
        onCancel={() => setAccountToDelete(null)}
      />
    </div>
  );
};
