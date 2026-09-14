from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.alert import AlertStatus, AlertSeverity


class InvestigationNoteCreate(BaseModel):
    note: str


class InvestigationNoteResponse(BaseModel):
    id: str
    alert_id: str
    author_name: str
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertStatusUpdate(BaseModel):
    status: AlertStatus


class AlertResponse(BaseModel):
    id: str
    organization_id: str
    device_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: AlertSeverity
    status: AlertStatus
    source_ip: Optional[str] = None
    affected_device_name: Optional[str] = None
    event_count: int
    first_seen: datetime
    last_seen: datetime
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertDetailResponse(AlertResponse):
    investigation_notes: List[InvestigationNoteResponse] = []
