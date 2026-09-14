export type AlertStatus = 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface OrganizationMembership {
  id: string;
  organization_id: string;
  organization_name: string;
  role: 'OWNER' | 'ANALYST' | 'VIEWER';
  created_at: string;
}

export interface Device {
  id: string;
  organization_id: string;
  hostname: string;
  ip_address?: string;
  os_type?: string;
  agent_version?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'REVOKED';
  last_seen_at?: string;
  created_at: string;
}

export interface DeviceRegisterResult extends Device {
  api_key: string;
}

export interface InvestigationNote {
  id: string;
  alert_id: string;
  author_name: string;
  note: string;
  created_at: string;
}

export interface Alert {
  id: string;
  organization_id: string;
  device_id?: string;
  assigned_user_id?: string;
  title: string;
  description?: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source_ip?: string;
  affected_device_name?: string;
  event_count: number;
  first_seen: string;
  last_seen: string;
  evidence?: any;
  created_at: string;
  updated_at: string;
  investigation_notes?: InvestigationNote[];
}

export interface AIAnalysis {
  id: string;
  alert_id: string;
  provider: string;
  model_name: string;
  summary: string;
  explanation: string;
  recommended_actions?: string[];
  is_mock: boolean;
  created_at: string;
}
