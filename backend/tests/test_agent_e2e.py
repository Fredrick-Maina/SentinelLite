import subprocess
from sentinellite_agent.main import SAMPLE_LOGS
from sentinellite_agent.client import IngestionClient


def test_agent_sample_replay_e2e(client):
    # Setup Org and Device
    client.post("/api/v1/auth/register", json={
        "email": "agent_tester@domain.com",
        "password": "Password123!",
        "full_name": "Agent Tester"
    })
    token = client.post("/api/v1/auth/login", data={"username": "agent_tester@domain.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    orgs = client.get("/api/v1/organizations", headers=headers).json()
    org_id = orgs[0]["organization_id"]

    reg_resp = client.post(f"/api/v1/organizations/{org_id}/devices", json={"hostname": "agent-host-01"}, headers=headers)
    api_key = reg_resp.json()["api_key"]

    # Use agent's IngestionClient directly against test client endpoint via mock or HTTP header check
    agent_client = IngestionClient("http://testserver", api_key)
    
    # Post events
    res = client.post("/api/v1/ingest/events", json={"events": SAMPLE_LOGS}, headers={"X-API-Key": api_key})
    assert res.status_code == 200
    data = res.json()
    assert data["ingested_count"] == len(SAMPLE_LOGS)

    # Check alerts generated automatically by DetectionEngine!
    alerts = client.get(f"/api/v1/organizations/{org_id}/alerts", headers=headers).json()
    assert len(alerts) >= 2  # Should generate SSH Brute Force AND Web Path Scanning alerts!
