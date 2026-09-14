import React, { useEffect, useState } from 'react';
import { Device, DeviceRegisterResult } from '../types';
import { api } from '../services/api';
import { Server, Plus, Key, ShieldOff, Check, Copy } from 'lucide-react';

interface DevicesPageProps {
  activeOrgId: string;
}

export const DevicesPage: React.FC<DevicesPageProps> = ({ activeOrgId }) => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [hostname, setHostname] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [osType, setOsType] = useState('');
  const [registeredKey, setRegisteredKey] = useState<DeviceRegisterResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadDevices = () => {
    if (!activeOrgId) return;
    setLoading(true);
    api.getDevices(activeOrgId)
      .then(setDevices)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDevices();
  }, [activeOrgId]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.registerDevice(activeOrgId, hostname, ipAddress, osType);
      setRegisteredKey(res);
      setHostname('');
      setIpAddress('');
      setOsType('');
      loadDevices();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRevoke = async (deviceId: string) => {
    if (!confirm('Are you sure you want to revoke this device? Its agent will no longer be able to send logs.')) return;
    try {
      await api.revokeDevice(activeOrgId, deviceId);
      loadDevices();
    } catch (err) {
      console.error(err);
    }
  };

  const copyKey = () => {
    if (!registeredKey) return;
    navigator.clipboard.writeText(registeredKey.api_key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Registered Collector Devices</h1>
          <p className="text-sm text-slate-400">Manage Python agents sending security logs to SentinelLite</p>
        </div>

        <button
          onClick={() => { setShowModal(true); setRegisteredKey(null); }}
          className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm rounded-lg flex items-center space-x-2 transition-colors shadow-md"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Device</span>
        </button>
      </div>

      {/* Device Cards List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-500">Loading devices...</div>
        ) : devices.length === 0 ? (
          <div className="col-span-full glass-card py-12 text-center text-slate-500 space-y-2">
            <Server className="w-8 h-8 mx-auto text-slate-600" />
            <div>No collector devices registered for this organization yet.</div>
          </div>
        ) : (
          devices.map(d => (
            <div key={d.id} className="glass-card p-6 space-y-4 relative">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Server className="w-5 h-5 text-emerald-400" />
                  <h3 className="font-bold text-slate-100">{d.hostname}</h3>
                </div>
                <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                  d.status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}>
                  {d.status}
                </span>
              </div>

              <div className="text-xs space-y-1 text-slate-400 font-mono">
                <div>IP Address: {d.ip_address || 'N/A'}</div>
                <div>OS Type: {d.os_type || 'Linux/Windows'}</div>
                <div>Agent Version: {d.agent_version || '0.1.0'}</div>
                <div>Last Seen: {d.last_seen_at ? new Date(d.last_seen_at).toLocaleString() : 'Never'}</div>
              </div>

              {d.status === 'ACTIVE' && (
                <div className="pt-2 border-t border-slate-800 flex justify-end">
                  <button
                    onClick={() => handleRevoke(d.id)}
                    className="text-xs text-rose-400 hover:text-rose-300 flex items-center space-x-1"
                  >
                    <ShieldOff className="w-3.5 h-3.5" />
                    <span>Revoke Credentials</span>
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Registration Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card w-full max-w-lg p-6 space-y-6 shadow-2xl">
            <h3 className="text-xl font-bold text-slate-100">Register Device Collector</h3>

            {!registeredKey ? (
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Hostname</label>
                  <input
                    type="text"
                    required
                    value={hostname}
                    onChange={e => setHostname(e.target.value)}
                    placeholder="prod-web-01"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">IP Address (Optional)</label>
                  <input
                    type="text"
                    value={ipAddress}
                    onChange={e => setIpAddress(e.target.value)}
                    placeholder="192.168.1.50"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">OS Type (Optional)</label>
                  <input
                    type="text"
                    value={osType}
                    onChange={e => setOsType(e.target.value)}
                    placeholder="Ubuntu 22.04 LTS"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-2">
                  <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-400 hover:text-slate-200 text-sm">
                    Cancel
                  </button>
                  <button type="submit" className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm rounded-lg">
                    Generate Agent Key
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-sm space-y-2">
                  <div className="flex items-center space-x-2 font-bold">
                    <Key className="w-5 h-5" />
                    <span>Agent API Key Generated</span>
                  </div>
                  <p className="text-xs text-slate-300">
                    Copy this secret key now. It will not be displayed again for security reasons.
                  </p>
                </div>

                <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between font-mono text-xs text-emerald-400 break-all">
                  <span>{registeredKey.api_key}</span>
                  <button onClick={copyKey} className="ml-2 p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded">
                    {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>

                <div className="flex justify-end">
                  <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-bold rounded-lg">
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
