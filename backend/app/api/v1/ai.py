from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.service import AISecurityAnalyst
from app.auth.deps import TenantAccessChecker, get_current_active_user
from app.database import get_db
from app.models.alert import Alert
from app.models.organization import Membership
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse

router = APIRouter()


@router.post("/organizations/{org_id}/alerts/{alert_id}/ai-analyze", response_model=AIAnalysisResponse)
def analyze_alert_with_ai(
    org_id: str,
    alert_id: str,
    request_in: AIAnalysisRequest = AIAnalysisRequest(),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """Trigger AI Security Analyst to generate grounded explanation and investigation steps for an alert."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.organization_id == org_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    analyst_service = AISecurityAnalyst(db)
    analysis = analyst_service.analyze_alert(alert, provider=request_in.provider or "mock")
    return analysis
