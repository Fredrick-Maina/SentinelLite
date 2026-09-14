from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AIAnalysisRequest(BaseModel):
    provider: Optional[str] = "mock"


class AIAnalysisResponse(BaseModel):
    id: str
    alert_id: str
    provider: str
    model_name: str
    summary: str
    explanation: str
    recommended_actions: Optional[List[str]] = None
    is_mock: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
