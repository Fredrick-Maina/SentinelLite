def test_report_generation_and_csv_export(client):
    # Setup user & org
    client.post("/api/v1/auth/register", json={
        "email": "report_admin@dev.com",
        "password": "Password123!",
        "full_name": "Report Admin"
    })
    token = client.post("/api/v1/auth/login", data={"username": "report_admin@dev.com", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get("/api/v1/organizations", headers=headers).json()[0]["organization_id"]

    # Generate Report
    gen_resp = client.post(
        f"/api/v1/organizations/{org_id}/reports",
        json={"title": "Q3 Executive Security Summary", "days": 30},
        headers=headers
    )
    assert gen_resp.status_code == 201
    report_data = gen_resp.json()
    assert report_data["title"] == "Q3 Executive Security Summary"
    report_id = report_data["id"]

    # Export CSV
    csv_resp = client.get(f"/api/v1/organizations/{org_id}/reports/{report_id}/export/csv", headers=headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "SentinelLite Executive Security Report" in csv_resp.text
