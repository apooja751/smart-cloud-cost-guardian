from app.services.health_score.calculator import calculate_cloud_health_score
from app.models.aws_account import AWSAccount

def test_cloud_health_score_calculation(db_session):
    account = db_session.query(AWSAccount).first()
    assert account is not None

    result = calculate_cloud_health_score(db_session, account.id)
    assert 0 <= result["overall_score"] <= 100
    assert result["grade"] in ["A", "B", "C", "D", "F"]

    breakdown = result["breakdown"]
    assert "cost_efficiency" in breakdown
    assert "resource_utilization" in breakdown
    assert "optimization_opportunities" in breakdown
    assert "budget_adherence" in breakdown
    assert "anomaly_health" in breakdown

    assert len(result["explanations"]) >= 1
