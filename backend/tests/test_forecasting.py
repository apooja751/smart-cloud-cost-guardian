from app.services.forecasting.forecaster import generate_cost_forecast
from app.models.aws_account import AWSAccount

def test_cost_forecaster_ml_output(db_session):
    account = db_session.query(AWSAccount).first()
    assert account is not None

    forecast = generate_cost_forecast(db_session, account.id)
    assert forecast["predicted_total"] > 0
    assert len(forecast["daily_forecasts"]) >= 1
    assert "Linear Trend" in forecast["model_used"]
