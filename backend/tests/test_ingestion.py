from app.services.normalizer import LogNormalizer
from app.models.event import EventSeverity


def test_log_normalizer_unit():
    # SSH Failed
    ssh_raw = "Mar 14 15:00:00 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 54321 ssh2"
    norm_ssh = LogNormalizer.normalize(ssh_raw, source_type="ssh")
    assert norm_ssh["event_type"] == "auth_failure"
    assert norm_ssh["severity"] == EventSeverity.MEDIUM
    assert norm_ssh["username"] == "admin"
    assert norm_ssh["source_ip"] == "192.168.1.100"

    # Web Nginx 404
    nginx_raw = '192.168.1.50 - - [14/Sep/2026:15:00:00 +0000] "GET /admin/config.php HTTP/1.1" 404 162'
    norm_web = LogNormalizer.normalize(nginx_raw, source_type="nginx")
    assert norm_web["event_type"] == "web_not_found"
    assert norm_web["source_ip"] == "192.168.1.50"
    assert norm_web["extra_metadata"]["status_code"] == 404


def test_ingest_events_api(client):
    # Setup user & org
    client.post("/api/v1/auth/register", json={
        "email": "agent_owner@dev.com",
        "password": "Password123!",
        "full_name": "Agent Admin"
    })
    token = client.post("/api/v1/auth/login", data={"username": "agent_owner@dev.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    orgs = client.get("/api/v1/organizations", headers=headers).json()
    org_id = orgs[0]["organization_id"]

    # Register device to get API Key
    reg_resp = client.post(f"/api/v1/organizations/{org_id}/devices", json={"hostname": "linux-agent-01"}, headers=headers)
    api_key = reg_resp.json()["api_key"]

    # Ingest logs using X-API-Key header
    agent_headers = {"X-API-Key": api_key}
    ingest_payload = {
        "events": [
            {
                "raw_message": "Failed password for root from 203.0.113.45 port 2222 ssh2",
                "source_type": "ssh"
            },
            {
                "raw_message": '203.0.113.45 - - [14/Sep/2026:15:05:00 +0000] "GET /etc/passwd HTTP/1.1" 404 200',
                "source_type": "nginx"
            }
        ]
    }

    ingest_resp = client.post("/api/v1/ingest/events", json=ingest_payload, headers=agent_headers)
    assert ingest_resp.status_code == 200
    res_data = ingest_resp.json()
    assert res_data["status"] == "ok"
    assert res_data["received_count"] == 2
    assert res_data["ingested_count"] == 2


def test_ingest_unauthorized_key(client):
    agent_headers = {"X-API-Key": "sl_ak_invalidkey00000000000000000"}
    ingest_payload = {"events": [{"raw_message": "test log"}]}
    ingest_resp = client.post("/api/v1/ingest/events", json=ingest_payload, headers=agent_headers)
    assert ingest_resp.status_code == 401
