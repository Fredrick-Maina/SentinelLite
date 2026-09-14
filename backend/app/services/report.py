import csv
import io
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.event import LogEvent
from app.models.alert import Alert, AlertStatus, AlertSeverity
from app.models.report import Report


class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_organization_report(self, organization_id: str, title: str, days: int = 30, user_id: str = None) -> Report:
        """Generate executive security report summary for an organization."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)

        # Count total events in range
        total_events = (
            self.db.query(func.count(LogEvent.id))
            .filter(
                LogEvent.organization_id == organization_id,
                LogEvent.timestamp >= start_time,
            )
            .scalar() or 0
        )

        # Count total alerts in range
        total_alerts = (
            self.db.query(func.count(Alert.id))
            .filter(
                Alert.organization_id == organization_id,
                Alert.created_at >= start_time,
            )
            .scalar() or 0
        )

        # Alert breakdown by severity
        severity_counts = {
            "CRITICAL": self.db.query(func.count(Alert.id)).filter(Alert.organization_id == organization_id, Alert.severity == AlertSeverity.CRITICAL, Alert.created_at >= start_time).scalar() or 0,
            "HIGH": self.db.query(func.count(Alert.id)).filter(Alert.organization_id == organization_id, Alert.severity == AlertSeverity.HIGH, Alert.created_at >= start_time).scalar() or 0,
            "MEDIUM": self.db.query(func.count(Alert.id)).filter(Alert.organization_id == organization_id, Alert.severity == AlertSeverity.MEDIUM, Alert.created_at >= start_time).scalar() or 0,
            "LOW": self.db.query(func.count(Alert.id)).filter(Alert.organization_id == organization_id, Alert.severity == AlertSeverity.LOW, Alert.created_at >= start_time).scalar() or 0,
        }

        # Resolved vs Unresolved
        resolved_count = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.organization_id == organization_id, Alert.status == AlertStatus.RESOLVED, Alert.created_at >= start_time)
            .scalar() or 0
        )

        # Top offending IPs
        top_ips_query = (
            self.db.query(Alert.source_ip, func.count(Alert.id).label("cnt"))
            .filter(Alert.organization_id == organization_id, Alert.source_ip.isnot(None), Alert.created_at >= start_time)
            .group_by(Alert.source_ip)
            .order_by(func.count(Alert.id).desc())
            .limit(5)
            .all()
        )
        top_ips = [{"ip": row[0], "alert_count": row[1]} for row in top_ips_query]

        summary_data = {
            "severity_breakdown": severity_counts,
            "resolved_alerts": resolved_count,
            "unresolved_alerts": total_alerts - resolved_count,
            "top_source_ips": top_ips,
            "days_covered": days,
        }

        report = Report(
            organization_id=organization_id,
            generated_by_user_id=user_id,
            title=title,
            period_start=start_time,
            period_end=end_time,
            total_events=total_events,
            total_alerts=total_alerts,
            summary_data=summary_data,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def export_report_csv(self, report: Report) -> str:
        """Export report summary into downloadable CSV string format."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["SentinelLite Executive Security Report"])
        writer.writerow(["Report Title", report.title])
        writer.writerow(["Organization ID", report.organization_id])
        writer.writerow(["Period Start", report.period_start.isoformat()])
        writer.writerow(["Period End", report.period_end.isoformat()])
        writer.writerow([])

        writer.writerow(["METRIC", "VALUE"])
        writer.writerow(["Total Logs Ingested", report.total_events])
        writer.writerow(["Total Security Alerts", report.total_alerts])
        
        breakdown = report.summary_data.get("severity_breakdown", {})
        writer.writerow(["Critical Alerts", breakdown.get("CRITICAL", 0)])
        writer.writerow(["High Severity Alerts", breakdown.get("HIGH", 0)])
        writer.writerow(["Medium Severity Alerts", breakdown.get("MEDIUM", 0)])
        writer.writerow(["Low Severity Alerts", breakdown.get("LOW", 0)])
        writer.writerow(["Resolved Alerts", report.summary_data.get("resolved_alerts", 0)])
        writer.writerow(["Unresolved Alerts", report.summary_data.get("unresolved_alerts", 0)])
        writer.writerow([])

        writer.writerow(["TOP OFFENDING SOURCE IP", "ALERT COUNT"])
        for item in report.summary_data.get("top_source_ips", []):
            writer.writerow([item.get("ip"), item.get("alert_count")])

        return output.getvalue()
