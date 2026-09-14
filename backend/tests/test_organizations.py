def get_auth_token(client, email, password):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": email.split("@")[0]
    })
    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def test_organization_creation_and_membership(client):
    token = get_auth_token(client, "owner@corp.com", "Password123!")
    headers = {"Authorization": f"Bearer {token}"}

    # List orgs (should contain initial registered org)
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200
    orgs = response.json()
    assert len(orgs) == 1
    assert orgs[0]["role"] == "OWNER"

    # Create second org
    create_resp = client.post("/api/v1/organizations", json={"name": "Second Corp"}, headers=headers)
    assert create_resp.status_code == 201
    new_org = create_resp.json()
    assert new_org["name"] == "Second Corp"

    # List orgs again
    response = client.get("/api/v1/organizations", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_tenant_isolation_and_permission_checks(client):
    owner_token = get_auth_token(client, "alice@org1.com", "Password123!")
    viewer_token = get_auth_token(client, "bob@org2.com", "Password123!")

    alice_headers = {"Authorization": f"Bearer {owner_token}"}
    bob_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Alice gets her orgs
    alice_orgs = client.get("/api/v1/organizations", headers=alice_headers).json()
    alice_org_id = alice_orgs[0]["organization_id"]

    # Bob tries to add member to Alice's organization -> should be forbidden (403)
    add_resp = client.post(
        f"/api/v1/organizations/{alice_org_id}/members",
        json={"user_email": "bob@org2.com", "role": "VIEWER"},
        headers=bob_headers
    )
    assert add_resp.status_code == 403
    assert "Access denied" in add_resp.json()["detail"]

    # Alice adds Bob to her organization as VIEWER
    add_resp_alice = client.post(
        f"/api/v1/organizations/{alice_org_id}/members",
        json={"user_email": "bob@org2.com", "role": "VIEWER"},
        headers=alice_headers
    )
    assert add_resp_alice.status_code == 200
    assert add_resp_alice.json()["role"] == "VIEWER"

    # Now Bob should see Alice's org in his org list as VIEWER
    bob_orgs = client.get("/api/v1/organizations", headers=bob_headers).json()
    assert len(bob_orgs) == 2
