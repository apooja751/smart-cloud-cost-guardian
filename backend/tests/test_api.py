from app.models.aws_account import AWSAccount

def test_api_endpoints_status(client, db_session):
    # Root
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "OPERATIONAL"

    # Health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "OK"

    # Accounts
    r_accs = client.get("/api/v1/aws/accounts")
    assert r_accs.status_code == 200
    assert len(r_accs.json()["data"]) > 0

    # Resources
    r_res = client.get("/api/v1/resources")
    assert r_res.status_code == 200
    assert len(r_res.json()["data"]) > 0

    # Costs Summary
    r_cost = client.get("/api/v1/costs/summary")
    assert r_cost.status_code == 200
    assert r_cost.json()["data"]["current_month_cost"] > 0

    # Recommendations
    r_recs = client.get("/api/v1/recommendations")
    assert r_recs.status_code == 200
    assert len(r_recs.json()["data"]) > 0

    # Health Score
    r_hs = client.get("/api/v1/health-score")
    assert r_hs.status_code == 200
    assert "overall_score" in r_hs.json()["data"]

    # Budgets
    r_budgets = client.get("/api/v1/budgets")
    assert r_budgets.status_code == 200

    # Assistant
    r_ai = client.post("/api/v1/assistant/ask", json={
        "question": "How can I reduce our cloud spend?"
    })
    assert r_ai.status_code == 200
    assert "answer" in r_ai.json()["data"]
