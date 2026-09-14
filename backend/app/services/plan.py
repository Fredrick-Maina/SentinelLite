from enum import Enum
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.device import Device, DeviceStatus


class PlanTier(str, Enum):
    FREE_TRIAL = "FREE_TRIAL"
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


PLAN_LIMITS: Dict[PlanTier, Dict[str, Any]] = {
    PlanTier.FREE_TRIAL: {
        "max_devices": 3,
        "retention_days": 7,
        "monthly_events": 50000,
        "ai_analyst": True,
    },
    PlanTier.STARTER: {
        "max_devices": 10,
        "retention_days": 30,
        "monthly_events": 500000,
        "ai_analyst": True,
    },
    PlanTier.PRO: {
        "max_devices": 50,
        "retention_days": 90,
        "monthly_events": 5000000,
        "ai_analyst": True,
    },
    PlanTier.ENTERPRISE: {
        "max_devices": 1000,
        "retention_days": 365,
        "monthly_events": 100000000,
        "ai_analyst": True,
    },
}


def check_device_limit(db: Session, organization_id: str, current_tier: PlanTier = PlanTier.STARTER):
    """Check if organization has reached its maximum allowed active registered devices for its plan tier."""
    limit = PLAN_LIMITS[current_tier]["max_devices"]
    active_device_count = (
        db.query(func.count(Device.id))
        .filter(Device.organization_id == organization_id, Device.status == DeviceStatus.ACTIVE)
        .scalar() or 0
    )

    if active_device_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Subscription tier limit reached: Your current plan '{current_tier.value}' allows up to {limit} active devices. Upgrade your subscription to register additional devices.",
        )
