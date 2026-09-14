from datetime import datetime, timezone
from app.detection.engine import DetectionEngine
from app.models.event import LogEvent, EventSeverity


def test_ssh_brute_force_detection(db):
    # Setup test data directly in DB
    org_id = "test-org-uuid"

    # Insert 5 failed SSH login events from same IP 198.51.100.22
    for i in range(5):
        event = LogEvent(
            organization_id=org_id,
            source_type="ssh",
            event_type="auth_failure",
            severity=EventSeverity.MEDIUM,
            timestamp=datetime.now(timezone.utc),
            username="root",
            source_ip="198.51.100.22",
            raw_message=f"Failed password for root from 198.51.100.22 port {5000+i} ssh2",
            detection_processed="PENDING"
        )
        db.add(event)
    db.commit()

    # Run detection engine
    engine = DetectionEngine(db)
    alerts = engine.evaluate_organization_events(org_id)

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.source_ip == "198.51.100.22"
    assert "SSH Brute-Force Attack" in alert.title
    assert alert.event_count == 5
    assert alert.severity.value == "HIGH"
