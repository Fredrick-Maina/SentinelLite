from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class ReportGenerateRequest(BaseModel):
    title: str
    days: Optional[int] = 30


class ReportResponse(BaseModel):
    id: str
    organization_id: str
    generated_by_user_id: Optional[str] = None
    title: str
    period_start: datetime
    period_end: datetime
    total_events: int
    total_alerts: int
    summary_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: str
    organization_id: str
    user_id: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
