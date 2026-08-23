from app.services.anomaly.detector import detect_cost_anomalies
from app.models.aws_account import AWSAccount

def test_anomaly_detection_engine(db_session):
    account = db_session.query(AWSAccount).first()
    assert account is not None

    anomalies = detect_cost_anomalies(db_session, account.id)
    assert isinstance(anomalies, list)
    if anomalies:
        first = anomalies[0]
        assert first.actual_cost >= 0
        assert first.severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
