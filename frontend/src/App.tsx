import React, { useEffect, useState } from 'react';
import { User, OrganizationMembership } from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { AlertsPage } from './pages/AlertsPage';
import { DevicesPage } from './pages/DevicesPage';
import './styles/main.css';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [memberships, setMemberships] = useState<OrganizationMembership[]>([]);
  const [activeOrgId, setActiveOrgId] = useState<string>('');
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'alerts' | 'devices'>('dashboard');
  const [loading, setLoading] = useState(true);

  const initAuth = async () => {
    setLoading(true);
    try {
      const u = await api.getMe();
      setUser(u);
      const orgs = await api.getOrganizations();
      setMemberships(orgs);
      if (orgs.length > 0) {
        setActiveOrgId(orgs[0].organization_id);
      }
    } catch (err) {
      setUser(null);
      localStorage.removeItem('sentinellite_token');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('sentinellite_token');
    if (token) {
      initAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('sentinellite_token');
    setUser(null);
    setMemberships([]);
    setActiveOrgId('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 font-mono text-sm">
        Initializing SentinelLite...
      </div>
    );
  }

  if (!user) {
    return authView === 'login' ? (
      <LoginPage onSuccess={initAuth} onNavigateRegister={() => setAuthView('register')} />
    ) : (
      <RegisterPage onSuccess={initAuth} onNavigateLogin={() => setAuthView('login')} />
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar
        user={user}
        memberships={memberships}
        activeOrgId={activeOrgId}
        onSelectOrg={setActiveOrgId}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLogout={handleLogout}
      />

      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <DashboardPage
            activeOrgId={activeOrgId}
            onNavigateAlerts={() => setActiveTab('alerts')}
            onNavigateDevices={() => setActiveTab('devices')}
          />
        )}

        {activeTab === 'alerts' && <AlertsPage activeOrgId={activeOrgId} />}

        {activeTab === 'devices' && <DevicesPage activeOrgId={activeOrgId} />}
      </main>
    </div>
  );
};
