def test_audit_logs(client):
    client.post("/api/v1/auth/register", json={
        "email": "auditor@dev.com",
        "password": "Password123!",
        "full_name": "Auditor User"
    })
    token = client.post("/api/v1/auth/login", data={"username": "auditor@dev.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get("/api/v1/organizations", headers=headers).json()[0]["organization_id"]

    # Register device to trigger DEVICE_REGISTERED audit log
    client.post(f"/api/v1/organizations/{org_id}/devices", json={"hostname": "audit-node-1"}, headers=headers)

    # Fetch audit logs
    audit_resp = client.get(f"/api/v1/organizations/{org_id}/audit-logs", headers=headers)
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 1
    actions = [l["action"] for l in logs]
    assert "DEVICE_REGISTERED" in actions
