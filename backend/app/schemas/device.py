from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.device import DeviceStatus


class DeviceRegisterRequest(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    agent_version: Optional[str] = "0.1.0"


class DeviceRegisterResponse(BaseModel):
    id: str
    organization_id: str
    hostname: str
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    agent_version: Optional[str] = None
    status: DeviceStatus
    api_key: str  # Raw API key provided ONCE upon registration
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceResponse(BaseModel):
    id: str
    organization_id: str
    hostname: str
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    agent_version: Optional[str] = None
    status: DeviceStatus
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
