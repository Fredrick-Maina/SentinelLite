import secrets
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import TenantAccessChecker, get_current_active_user
from app.auth.security import get_password_hash
from app.database import get_db
from app.models.device import AgentCredential, Device, DeviceStatus
from app.models.organization import Membership
from app.models.user import User, UserRole
from app.schemas.device import DeviceRegisterRequest, DeviceRegisterResponse, DeviceResponse
from app.services.plan import check_device_limit, PlanTier
from app.services.audit import record_audit_event

router = APIRouter()


@router.post("/organizations/{org_id}/devices", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_device(
    org_id: str,
    device_in: DeviceRegisterRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER, UserRole.ANALYST])),
) -> Any:
    """Register a new device for an organization, enforcing subscription tier device limits."""
    # Check plan limit
    check_device_limit(db, organization_id=org_id, current_tier=PlanTier.STARTER)

    device = Device(
        organization_id=org_id,
        hostname=device_in.hostname,
        ip_address=device_in.ip_address,
        os_type=device_in.os_type,
        agent_version=device_in.agent_version,
        status=DeviceStatus.ACTIVE,
    )
    db.add(device)
    db.flush()

    raw_api_key = f"sl_ak_{secrets.token_hex(16)}"
    key_prefix = raw_api_key[:12]
    key_hash = get_password_hash(raw_api_key)

    credential = AgentCredential(
        device_id=device.id,
        api_key_prefix=key_prefix,
        api_key_hash=key_hash,
        is_revoked=False,
    )
    db.add(credential)
    db.commit()
    db.refresh(device)

    record_audit_event(
        db,
        organization_id=org_id,
        action="DEVICE_REGISTERED",
        user_id=current_user.id,
        target_type="device",
        target_id=device.id,
        details={"hostname": device.hostname},
    )

    return DeviceRegisterResponse(
        id=device.id,
        organization_id=device.organization_id,
        hostname=device.hostname,
        ip_address=device.ip_address,
        os_type=device.os_type,
        agent_version=device.agent_version,
        status=device.status,
        api_key=raw_api_key,
        created_at=device.created_at,
    )


@router.get("/organizations/{org_id}/devices", response_model=List[DeviceResponse])
def list_devices(
    org_id: str,
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker()),
) -> Any:
    """List all registered devices in an organization."""
    devices = db.query(Device).filter(Device.organization_id == org_id).all()
    return devices


@router.delete("/organizations/{org_id}/devices/{device_id}/revoke", status_code=status.HTTP_200_OK)
def revoke_device(
    org_id: str,
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER])),
) -> Any:
    """Revoke all API keys and mark device status as REVOKED."""
    device = (
        db.query(Device)
        .filter(Device.id == device_id, Device.organization_id == org_id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    device.status = DeviceStatus.REVOKED
    for cred in device.credentials:
        cred.is_revoked = True

    db.commit()

    record_audit_event(
        db,
        organization_id=org_id,
        action="DEVICE_REVOKED",
        user_id=current_user.id,
        target_type="device",
        target_id=device.id,
        details={"hostname": device.hostname},
    )

    return {"message": f"Device '{device.hostname}' credentials have been revoked"}
