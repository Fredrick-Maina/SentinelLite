from app.services.plan import check_device_limit, PlanTier
from app.models.device import Device, DeviceStatus
import pytest
from fastapi import HTTPException


def test_plan_device_limit_enforcement(db):
    org_id = "test-subscription-org"

    # Insert devices up to FREE_TRIAL limit (3 devices)
    for i in range(3):
        dev = Device(
            organization_id=org_id,
            hostname=f"trial-host-{i}",
            status=DeviceStatus.ACTIVE
        )
        db.add(dev)
    db.commit()

    # Attempting 4th device on FREE_TRIAL tier should raise 402 Payment Required
    with pytest.raises(HTTPException) as exc_info:
        check_device_limit(db, org_id, current_tier=PlanTier.FREE_TRIAL)

    assert exc_info.value.status_code == 402
    assert "Subscription tier limit reached" in exc_info.value.detail
