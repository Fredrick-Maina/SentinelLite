import React, { useEffect, useState } from 'react';
import { Alert, Device } from '../types';
import { api } from '../services/api';
import { ShieldAlert, Server, Activity, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';

interface DashboardPageProps {
  activeOrgId: string;
  onNavigateAlerts: () => void;
  onNavigateDevices: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  activeOrgId,
  onNavigateAlerts,
  onNavigateDevices,
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setLoading(true);
    Promise.all([
      api.getAlerts(activeOrgId),
      api.getDevices(activeOrgId)
    ])
      .then(([alertsData, devicesData]) => {
        setAlerts(alertsData);
        setDevices(devicesData);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [activeOrgId]);

  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL').length;
  const highCount = alerts.filter(a => a.severity === 'HIGH').length;
  const mediumCount = alerts.filter(a => a.severity === 'MEDIUM').length;
  const lowCount = alerts.filter(a => a.severity === 'LOW').length;
  const activeDevicesCount = devices.filter(d => d.status === 'ACTIVE').length;

  // Aggregate top source IPs
  const ipCounts: { [ip: string]: number } = {};
  alerts.forEach(a => {
    if (a.source_ip) {
      ipCounts[a.source_ip] = (ipCounts[a.source_ip] || 0) + a.event_count;
    }
  });

  const topIPs = Object.entries(ipCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400">
        <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-emerald-400" />
        Loading Security Dashboard...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Security Command Center</h1>
          <p className="text-sm text-slate-400">Real-time threat monitoring and device posture</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Critical Alerts</span>
            <ShieldAlert className="w-5 h-5 text-rose-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100 mt-2">{criticalCount}</div>
          <div className="text-xs text-rose-400 mt-1 font-mono">Immediate attention required</div>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">High & Med Alerts</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100 mt-2">{highCount + mediumCount}</div>
          <div className="text-xs text-slate-400 mt-1 font-mono">Total High: {highCount} | Med: {mediumCount}</div>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monitored Devices</span>
            <Server className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100 mt-2">{activeDevicesCount}</div>
          <div className="text-xs text-emerald-400 mt-1 font-mono">Active Agent Collectors</div>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-blue-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Alerts</span>
            <CheckCircle2 className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100 mt-2">{alerts.length}</div>
          <div className="text-xs text-slate-400 mt-1 font-mono">Low Severity: {lowCount}</div>
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Alerts Feed (2 cols) */}
        <div className="lg:col-span-2 glass-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="font-semibold text-slate-200">Recent Security Activity</h3>
            <button
              onClick={onNavigateAlerts}
              className="text-xs text-emerald-400 hover:underline flex items-center space-x-1"
            >
              <span>View All Alerts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {alerts.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">
              No security alerts detected for this organization yet.
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className="p-4 bg-slate-900/80 border border-slate-800/80 rounded-xl flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                        alert.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        alert.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}>
                        {alert.severity}
                      </span>
                      <span className="font-semibold text-slate-200 text-sm">{alert.title}</span>
                    </div>
                    <p className="text-xs text-slate-400">{alert.description}</p>
                  </div>
                  <div className="text-right text-xs text-slate-500 font-mono">
                    <div>{alert.event_count} events</div>
                    <div>{new Date(alert.last_seen).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Offending IPs Table (1 col) */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="font-semibold text-slate-200">Top Suspicious IPs</h3>
          </div>

          {topIPs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">No IP threat data available.</div>
          ) : (
            <div className="space-y-2">
              {topIPs.map(([ip, count], i) => (
                <div key={ip} className="flex items-center justify-between p-2.5 bg-slate-900/50 rounded-lg text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-500 font-mono">#{i + 1}</span>
                    <span className="font-mono text-emerald-400 font-medium">{ip}</span>
                  </div>
                  <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300 font-mono">
                    {count} events
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="pt-4 border-t border-slate-800">
            <button
              onClick={onNavigateDevices}
              className="w-full text-center text-xs text-slate-400 hover:text-emerald-400 py-2 border border-slate-800 rounded-lg hover:border-emerald-500/30 transition-colors"
            >
              Manage Registered Agent Collectors →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
