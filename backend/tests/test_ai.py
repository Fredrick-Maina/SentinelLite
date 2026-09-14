from app.ai.service import AISecurityAnalyst


def test_ai_redaction_unit():
    analyst = AISecurityAnalyst(None)
    raw_text = '{"username": "admin", "password": "supersecretpassword123", "token": "secrettoken456"}'
    redacted = analyst.redact_sensitive_evidence(raw_text)
    assert "supersecretpassword123" not in redacted
    assert "[REDACTED]" in redacted


def test_ai_analysis_api(client):
    # Register & setup device
    client.post("/api/v1/auth/register", json={
        "email": "ai_user@corp.com",
        "password": "Password123!",
        "full_name": "AI Tester"
    })
    token = client.post("/api/v1/auth/login", data={"username": "ai_user@corp.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get("/api/v1/organizations", headers=headers).json()[0]["organization_id"]

    dev_data = client.post(f"/api/v1/organizations/{org_id}/devices", json={"hostname": "ai-server"}, headers=headers).json()
    agent_headers = {"X-API-Key": dev_data["api_key"]}

    # Ingest logs to trigger SSH Brute force alert
    events = [
        {"raw_message": "Failed password for invalid user admin from 198.51.100.77 port 22 ssh2", "source_type": "ssh"}
        for _ in range(5)
    ]
    client.post("/api/v1/ingest/events", json={"events": events}, headers=agent_headers)

    # Get generated alert
    alerts = client.get(f"/api/v1/organizations/{org_id}/alerts", headers=headers).json()
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    # Trigger AI Analysis
    ai_resp = client.post(f"/api/v1/organizations/{org_id}/alerts/{alert_id}/ai-analyze", json={"provider": "mock"}, headers=headers)
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()
    assert ai_data["alert_id"] == alert_id
    assert "SSH login attempts" in ai_data["summary"]
    assert len(ai_data["recommended_actions"]) > 0
    assert ai_data["is_mock"] is True
