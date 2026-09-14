def get_auth_context(client, email="owner@dev.com"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Dev Owner",
        "organization_name": "Dev Sec Corp"
    })
    token = client.post("/api/v1/auth/login", data={"username": email, "password": "SecurePassword123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    orgs = client.get("/api/v1/organizations", headers=headers).json()
    return token, headers, orgs[0]["organization_id"]


def test_register_and_list_device(client):
    token, headers, org_id = get_auth_context(client, "device_admin@corp.com")

    # Register device
    reg_payload = {
        "hostname": "prod-web-01",
        "ip_address": "192.168.1.10",
        "os_type": "Ubuntu 22.04 LTS",
        "agent_version": "0.1.0"
    }
    response = client.post(f"/api/v1/organizations/{org_id}/devices", json=reg_payload, headers=headers)
    assert response.status_code == 201
    dev_data = response.json()
    assert dev_data["hostname"] == "prod-web-01"
    assert "api_key" in dev_data
    assert dev_data["api_key"].startswith("sl_ak_")
    device_id = dev_data["id"]

    # List devices
    list_resp = client.get(f"/api/v1/organizations/{org_id}/devices", headers=headers)
    assert list_resp.status_code == 200
    devices = list_resp.json()
    assert len(devices) == 1
    assert devices[0]["id"] == device_id

    # Revoke device
    revoke_resp = client.delete(f"/api/v1/organizations/{org_id}/devices/{device_id}/revoke", headers=headers)
    assert revoke_resp.status_code == 200

    # Verify device status is REVOKED
    list_after_revoke = client.get(f"/api/v1/organizations/{org_id}/devices", headers=headers).json()
    assert list_after_revoke[0]["status"] == "REVOKED"
