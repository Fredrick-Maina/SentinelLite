from datetime import datetime, timezone
from typing import Any, Tuple
from fastapi import APIRouter, Header, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import verify_password
from app.database import get_db
from app.detection.engine import DetectionEngine
from app.models.device import AgentCredential, Device, DeviceStatus
from app.models.event import LogEvent
from app.schemas.ingest import IngestLogsRequest, IngestLogsResponse
from app.services.normalizer import LogNormalizer

router = APIRouter()


def authenticate_agent(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Tuple[Device, AgentCredential]:
    """Authenticate an agent request using its raw API key header X-API-Key."""
    if not x_api_key or not x_api_key.startswith("sl_ak_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing agent API key header",
        )

    key_prefix = x_api_key[:12]
    credentials = (
        db.query(AgentCredential)
        .filter(
            AgentCredential.api_key_prefix == key_prefix,
            AgentCredential.is_revoked == False,
        )
        .all()
    )

    matching_cred = None
    for cred in credentials:
        if verify_password(x_api_key, cred.api_key_hash):
            matching_cred = cred
            break

    if not matching_cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or credential revoked",
        )

    device = db.query(Device).filter(Device.id == matching_cred.device_id).first()
    if not device or device.status == DeviceStatus.REVOKED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device is inactive or revoked",
        )

    return device, matching_cred


@router.post("/events", response_model=IngestLogsResponse)
def ingest_log_events(
    payload: IngestLogsRequest,
    db: Session = Depends(get_db),
    agent_info: Tuple[Device, AgentCredential] = Depends(authenticate_agent),
) -> Any:
    """Ingest a batch of raw log events sent by an authenticated agent and trigger detection."""
    device, cred = agent_info
    received_count = len(payload.events)
    ingested_count = 0
    errors = []

    now = datetime.now(timezone.utc)
    device.last_seen_at = now
    cred.last_used_at = now

    events_to_create = []

    for idx, item in enumerate(payload.events):
        try:
            norm = LogNormalizer.normalize(
                raw_message=item.raw_message,
                source_type=item.source_type or "generic",
                default_timestamp=item.timestamp or now,
                default_hostname=item.hostname or device.hostname,
            )

            log_event = LogEvent(
                organization_id=device.organization_id,
                device_id=device.id,
                hostname=norm["hostname"],
                source_type=norm["source_type"],
                event_type=norm["event_type"],
                severity=norm["severity"],
                timestamp=norm["timestamp"],
                received_at=now,
                username=norm["username"],
                source_ip=norm["source_ip"],
                destination_ip=norm["destination_ip"],
                destination_port=norm["destination_port"],
                message=norm["message"],
                raw_message=norm["raw_message"],
                extra_metadata=norm["extra_metadata"],
                detection_processed="PENDING",
            )
            events_to_create.append(log_event)
            ingested_count += 1
        except Exception as e:
            errors.append(f"Event #{idx}: {str(e)}")

    if events_to_create:
        db.add_all(events_to_create)
        db.commit()

        # Trigger Detection Engine on newly ingested events
        engine = DetectionEngine(db)
        engine.evaluate_organization_events(device.organization_id)

    return IngestLogsResponse(
        status="ok" if ingested_count > 0 else "error",
        received_count=received_count,
        ingested_count=ingested_count,
        failed_count=len(errors),
        errors=errors if errors else None,
    )
