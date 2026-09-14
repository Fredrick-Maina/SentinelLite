from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.deps import TenantAccessChecker, get_current_active_user
from app.database import get_db
from app.models.organization import Membership
from app.models.report import Report
from app.models.user import User, UserRole
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.report import ReportGenerator
from app.services.audit import record_audit_event

router = APIRouter()


@router.post("/organizations/{org_id}/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    org_id: str,
    request_in: ReportGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER, UserRole.ANALYST])),
) -> Any:
    """Generate an executive security report summary."""
    generator = ReportGenerator(db)
    report = generator.generate_organization_report(
        organization_id=org_id,
        title=request_in.title,
        days=request_in.days or 30,
        user_id=current_user.id,
    )

    record_audit_event(
        db,
        organization_id=org_id,
        action="REPORT_GENERATED",
        user_id=current_user.id,
        target_type="report",
        target_id=report.id,
        details={"title": report.title, "days": request_in.days},
    )

    return report


@router.get("/organizations/{org_id}/reports", response_model=List[ReportResponse])
def list_reports(
    org_id: str,
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """List all generated reports for an organization."""
    reports = db.query(Report).filter(Report.organization_id == org_id).order_by(Report.created_at.desc()).all()
    return reports


@router.get("/organizations/{org_id}/reports/{report_id}/export/csv")
def export_report_csv(
    org_id: str,
    report_id: str,
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """Export executive security report as downloadable CSV file."""
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.organization_id == org_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    generator = ReportGenerator(db)
    csv_content = generator.export_report_csv(report)

    filename = f"sentinellite_report_{report.id[:8]}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
