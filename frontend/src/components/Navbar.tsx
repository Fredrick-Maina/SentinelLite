import React from 'react';
import { OrganizationMembership, User } from '../types';
import { Shield, Server, Bell, LogOut, Building } from 'lucide-react';

interface NavbarProps {
  user: User | null;
  memberships: OrganizationMembership[];
  activeOrgId: string;
  onSelectOrg: (id: string) => void;
  activeTab: 'dashboard' | 'alerts' | 'devices';
  onTabChange: (tab: 'dashboard' | 'alerts' | 'devices') => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  memberships,
  activeOrgId,
  onSelectOrg,
  activeTab,
  onTabChange,
  onLogout,
}) => {
  return (
    <nav className="glass-nav sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-8">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onTabChange('dashboard')}>
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
            <Shield className="w-6 h-6" />
          </div>
          <span className="font-bold text-xl tracking-tight text-slate-100">
            Sentinel<span className="text-emerald-400">Lite</span>
          </span>
        </div>

        {/* Navigation Tabs */}
        {user && (
          <div className="flex items-center space-x-2 bg-slate-900/60 p-1 border border-slate-800 rounded-lg">
            <button
              onClick={() => onTabChange('dashboard')}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
                activeTab === 'dashboard' ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => onTabChange('alerts')}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all flex items-center space-x-1.5 ${
                activeTab === 'alerts' ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Bell className="w-4 h-4" />
              <span>Alerts</span>
            </button>
            <button
              onClick={() => onTabChange('devices')}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all flex items-center space-x-1.5 ${
                activeTab === 'devices' ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Server className="w-4 h-4" />
              <span>Devices</span>
            </button>
          </div>
        )}
      </div>

      {user && (
        <div className="flex items-center space-x-4">
          {/* Tenant / Organization Switcher */}
          {memberships.length > 0 && (
            <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-sm">
              <Building className="w-4 h-4 text-emerald-400" />
              <select
                value={activeOrgId}
                onChange={(e) => onSelectOrg(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
              >
                {memberships.map((m) => (
                  <option key={m.organization_id} value={m.organization_id} className="bg-slate-900 text-slate-100">
                    {m.organization_name} ({m.role})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* User Profile info */}
          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">{user.email}</div>
          </div>

          <button
            onClick={onLogout}
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
            title="Log Out"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      )}
    </nav>
  );
};
