from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.event import LogEvent, EventSeverity
from app.models.detection import DetectionRule
from app.models.alert import Alert, AlertEvent, AlertSeverity, AlertStatus


class DetectionEngine:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_organization_events(self, organization_id: str) -> List[Alert]:
        """Evaluate pending log events for an organization against detection rules."""
        pending_events = (
            self.db.query(LogEvent)
            .filter(
                LogEvent.organization_id == organization_id,
                LogEvent.detection_processed == "PENDING",
            )
            .all()
        )

        if not pending_events:
            return []

        generated_alerts = []

        # 1. Evaluate SSH Brute-Force & Failed Login Rules
        brute_force_alerts = self._check_ssh_brute_force(organization_id)
        generated_alerts.extend(brute_force_alerts)

        # 2. Evaluate Web Path Scanning Rule
        web_scan_alerts = self._check_web_scanning(organization_id)
        generated_alerts.extend(web_scan_alerts)

        # Mark processed events
        for event in pending_events:
            event.detection_processed = "PROCESSED"

        self.db.commit()
        return generated_alerts

    def _check_ssh_brute_force(self, organization_id: str, time_window_minutes: int = 5, threshold: int = 3) -> List[Alert]:
        """Detect repeated failed authentication attempts from the same source IP."""
        time_cutoff = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)

        results = (
            self.db.query(
                LogEvent.source_ip,
                LogEvent.device_id,
                func.count(LogEvent.id).label("fail_count"),
                func.min(LogEvent.timestamp).label("first_seen"),
                func.max(LogEvent.timestamp).label("last_seen"),
            )
            .filter(
                LogEvent.organization_id == organization_id,
                LogEvent.event_type == "auth_failure",
                LogEvent.timestamp >= time_cutoff,
                LogEvent.source_ip.isnot(None),
            )
            .group_by(LogEvent.source_ip, LogEvent.device_id)
            .having(func.count(LogEvent.id) >= threshold)
            .all()
        )

        alerts_created = []

        for row in results:
            source_ip, device_id, fail_count, first_seen, last_seen = row

            # Check existing active alert to avoid duplicate alerts (Deduplication)
            existing_alert = (
                self.db.query(Alert)
                .filter(
                    Alert.organization_id == organization_id,
                    Alert.source_ip == source_ip,
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING]),
                )
                .first()
            )

            if existing_alert:
                existing_alert.event_count += fail_count
                existing_alert.last_seen = max(existing_alert.last_seen, last_seen)
                alerts_created.append(existing_alert)
            else:
                alert = Alert(
                    organization_id=organization_id,
                    device_id=device_id,
                    title=f"Possible SSH Brute-Force Attack from {source_ip}",
                    description=f"Detected {fail_count} failed SSH authentication attempts from IP address {source_ip} within {time_window_minutes} minutes.",
                    severity=AlertSeverity.HIGH if fail_count < 10 else AlertSeverity.CRITICAL,
                    status=AlertStatus.NEW,
                    source_ip=source_ip,
                    event_count=fail_count,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    evidence={
                        "rule_code": "SSH_BRUTE_FORCE",
                        "fail_count": fail_count,
                        "time_window_minutes": time_window_minutes,
                    },
                )
                self.db.add(alert)
                alerts_created.append(alert)

        return alerts_created

    def _check_web_scanning(self, organization_id: str, time_window_minutes: int = 5, threshold: int = 4) -> List[Alert]:
        """Detect repeated 404/not found web requests from the same source IP."""
        time_cutoff = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)

        results = (
            self.db.query(
                LogEvent.source_ip,
                LogEvent.device_id,
                func.count(LogEvent.id).label("scan_count"),
                func.min(LogEvent.timestamp).label("first_seen"),
                func.max(LogEvent.timestamp).label("last_seen"),
            )
            .filter(
                LogEvent.organization_id == organization_id,
                LogEvent.event_type == "web_not_found",
                LogEvent.timestamp >= time_cutoff,
                LogEvent.source_ip.isnot(None),
            )
            .group_by(LogEvent.source_ip, LogEvent.device_id)
            .having(func.count(LogEvent.id) >= threshold)
            .all()
        )

        alerts_created = []

        for row in results:
            source_ip, device_id, scan_count, first_seen, last_seen = row

            existing_alert = (
                self.db.query(Alert)
                .filter(
                    Alert.organization_id == organization_id,
                    Alert.source_ip == source_ip,
                    Alert.title.like("Possible Web Path Scanning%"),
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING]),
                )
                .first()
            )

            if existing_alert:
                existing_alert.event_count += scan_count
                existing_alert.last_seen = max(existing_alert.last_seen, last_seen)
                alerts_created.append(existing_alert)
            else:
                alert = Alert(
                    organization_id=organization_id,
                    device_id=device_id,
                    title=f"Possible Web Path Scanning from {source_ip}",
                    description=f"Detected {scan_count} missing page (404) requests from IP address {source_ip} targeting web resources.",
                    severity=AlertSeverity.MEDIUM,
                    status=AlertStatus.NEW,
                    source_ip=source_ip,
                    event_count=scan_count,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    evidence={
                        "rule_code": "WEB_PATH_SCANNING",
                        "scan_count": scan_count,
                        "time_window_minutes": time_window_minutes,
                    },
                )
                self.db.add(alert)
                alerts_created.append(alert)

        return alerts_created
