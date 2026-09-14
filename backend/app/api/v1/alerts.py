from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.auth.deps import TenantAccessChecker, get_current_active_user
from app.database import get_db
from app.models.alert import Alert, AlertStatus, AlertSeverity, InvestigationNote
from app.models.organization import Membership
from app.models.user import User, UserRole
from app.schemas.alert import (
    AlertDetailResponse,
    AlertResponse,
    AlertStatusUpdate,
    InvestigationNoteCreate,
    InvestigationNoteResponse,
)

router = APIRouter()


@router.get("/organizations/{org_id}/alerts", response_model=List[AlertResponse])
def list_alerts(
    org_id: str,
    status_filter: Optional[AlertStatus] = Query(None, alias="status"),
    severity_filter: Optional[AlertSeverity] = Query(None, alias="severity"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """List security alerts for an organization with optional status, severity, and search filtering."""
    query = db.query(Alert).filter(Alert.organization_id == org_id)

    if status_filter:
        query = query.filter(Alert.status == status_filter)

    if severity_filter:
        query = query.filter(Alert.severity == severity_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Alert.title.ilike(search_pattern))
            | (Alert.description.ilike(search_pattern))
            | (Alert.source_ip.ilike(search_pattern))
        )

    alerts = query.order_by(desc(Alert.last_seen)).offset(offset).limit(limit).all()
    return alerts


@router.get("/organizations/{org_id}/alerts/{alert_id}", response_model=AlertDetailResponse)
def get_alert_detail(
    org_id: str,
    alert_id: str,
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """Get detailed information about a specific security alert including investigation notes."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.organization_id == org_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.patch("/organizations/{org_id}/alerts/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    org_id: str,
    alert_id: str,
    status_in: AlertStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER, UserRole.ANALYST])),
) -> Any:
    """Update alert triage status (NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, FALSE_POSITIVE)."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.organization_id == org_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.status = status_in.status
    if not alert.assigned_user_id:
        alert.assigned_user_id = current_user.id

    db.commit()
    db.refresh(alert)
    return alert


@router.post("/organizations/{org_id}/alerts/{alert_id}/notes", response_model=InvestigationNoteResponse, status_code=status.HTTP_201_CREATED)
def add_investigation_note(
    org_id: str,
    alert_id: str,
    note_in: InvestigationNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER, UserRole.ANALYST])),
) -> Any:
    """Add an analyst investigation note to an alert."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.organization_id == org_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    note = InvestigationNote(
        alert_id=alert.id,
        user_id=current_user.id,
        author_name=current_user.full_name or current_user.email,
        note=note_in.note,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return note
