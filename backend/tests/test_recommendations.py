from app.services.recommendations.engine import run_recommendation_engine
from app.models.aws_account import AWSAccount

def test_recommendation_engine_generates_rules(db_session):
    account = db_session.query(AWSAccount).first()
    assert account is not None

    recs = run_recommendation_engine(db_session, account.id)
    assert len(recs) > 0

    categories = {r.category for r in recs}
    assert any("Compute" in c or "Storage" in c or "Database" in c or "Network" in c for c in categories)

    for r in recs:
        assert r.estimated_monthly_savings > 0
        assert 0.0 <= r.confidence <= 1.0
        assert r.severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert len(r.evidence) > 0
        assert len(r.title) > 0
