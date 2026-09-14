def test_alerts_api_workflow(client):
    # Register user & org
    client.post("/api/v1/auth/register", json={
        "email": "analyst@cyber.com",
        "password": "Password123!",
        "full_name": "SOC Analyst"
    })
    token = client.post("/api/v1/auth/login", data={"username": "analyst@cyber.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    orgs = client.get("/api/v1/organizations", headers=headers).json()
    org_id = orgs[0]["organization_id"]

    # Register device & get API Key
    dev_data = client.post(f"/api/v1/organizations/{org_id}/devices", json={"hostname": "server-01"}, headers=headers).json()
    agent_headers = {"X-API-Key": dev_data["api_key"]}

    # Ingest 4 failed SSH login logs from 203.0.113.99 to trigger alert
    events = [
        {"raw_message": "Failed password for admin from 203.0.113.99 port 22 ssh2", "source_type": "ssh"}
        for _ in range(4)
    ]
    client.post("/api/v1/ingest/events", json={"events": events}, headers=agent_headers)

    # Fetch alerts for org
    alerts_resp = client.get(f"/api/v1/organizations/{org_id}/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) == 1
    alert_id = alerts[0]["id"]
    assert alerts[0]["status"] == "NEW"

    # Update alert status to INVESTIGATING
    patch_resp = client.patch(
        f"/api/v1/organizations/{org_id}/alerts/{alert_id}/status",
        json={"status": "INVESTIGATING"},
        headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "INVESTIGATING"

    # Add investigation note
    note_resp = client.post(
        f"/api/v1/organizations/{org_id}/alerts/{alert_id}/notes",
        json={"note": "Investigating source IP 203.0.113.99 against threat intelligence feed."},
        headers=headers
    )
    assert note_resp.status_code == 201
    assert "threat intelligence" in note_resp.json()["note"]

    # Get alert detail
    detail_resp = client.get(f"/api/v1/organizations/{org_id}/alerts/{alert_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["investigation_notes"]) == 1
