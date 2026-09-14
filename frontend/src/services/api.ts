import { Alert, AlertStatus, AIAnalysis, Device, DeviceRegisterResult, OrganizationMembership, User } from '../types';

const API_BASE = '/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('sentinellite_token');
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

export const api = {
  async register(email: string, password: string, full_name?: string, organization_name?: string): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name, organization_name }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(username: string, password: string): Promise<string> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Invalid email or password');
    }
    const data = await res.json();
    localStorage.setItem('sentinellite_token', data.access_token);
    return data.access_token;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Unauthorized');
    return res.json();
  },

  async getOrganizations(): Promise<OrganizationMembership[]> {
    const res = await fetch(`${API_BASE}/organizations`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch organizations');
    return res.json();
  },

  async getDevices(orgId: string): Promise<Device[]> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/devices`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch devices');
    return res.json();
  },

  async registerDevice(orgId: string, hostname: string, ip_address?: string, os_type?: string): Promise<DeviceRegisterResult> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/devices`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ hostname, ip_address, os_type, agent_version: '0.1.0' }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to register device');
    }
    return res.json();
  },

  async revokeDevice(orgId: string, deviceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/devices/${deviceId}/revoke`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to revoke device');
  },

  async getAlerts(orgId: string, statusFilter?: string, severityFilter?: string): Promise<Alert[]> {
    let url = `${API_BASE}/organizations/${orgId}/alerts?limit=100`;
    if (statusFilter) url += `&status=${statusFilter}`;
    if (severityFilter) url += `&severity=${severityFilter}`;
    
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async getAlertDetail(orgId: string, alertId: string): Promise<Alert> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/alerts/${alertId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alert details');
    return res.json();
  },

  async updateAlertStatus(orgId: string, alertId: string, status: AlertStatus): Promise<Alert> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/alerts/${alertId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update alert status');
    return res.json();
  },

  async addInvestigationNote(orgId: string, alertId: string, note: string): Promise<any> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/alerts/${alertId}/notes`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ note }),
    });
    if (!res.ok) throw new Error('Failed to add note');
    return res.json();
  },

  async runAIAnalysis(orgId: string, alertId: string): Promise<AIAnalysis> {
    const res = await fetch(`${API_BASE}/organizations/${orgId}/alerts/${alertId}/ai-analyze`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ provider: 'mock' }),
    });
    if (!res.ok) throw new Error('AI analysis failed');
    return res.json();
  }
};
