from typing import Any, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.deps import TenantAccessChecker
from app.database import get_db
from app.models.audit import AuditLog
from app.models.organization import Membership
from app.models.user import UserRole
from app.schemas.report import AuditLogResponse

router = APIRouter()


@router.get("/organizations/{org_id}/audit-logs", response_model=List[AuditLogResponse])
def get_organization_audit_logs(
    org_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER, UserRole.ANALYST])),
) -> Any:
    """Retrieve immutable audit logs for an organization."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == org_id)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return logs
