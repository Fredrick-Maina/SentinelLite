from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.event import EventSeverity


class RawLogItem(BaseModel):
    raw_message: str
    source_type: Optional[str] = "generic"  # ssh, syslog, nginx, apache, json
    timestamp: Optional[datetime] = None
    hostname: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class IngestLogsRequest(BaseModel):
    events: List[RawLogItem] = Field(..., max_length=1000)


class NormalizedEventSchema(BaseModel):
    id: str
    organization_id: str
    device_id: Optional[str] = None
    hostname: Optional[str] = None
    source_type: str
    event_type: str
    severity: EventSeverity
    timestamp: datetime
    received_at: datetime
    username: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None
    message: Optional[str] = None
    raw_message: str

    model_config = ConfigDict(from_attributes=True)


class IngestLogsResponse(BaseModel):
    status: str
    received_count: int
    ingested_count: int
    failed_count: int
    errors: Optional[List[str]] = None
