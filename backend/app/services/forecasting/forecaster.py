import datetime
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.cost import CostRecord
from app.models.forecast import Forecast

def generate_cost_forecast(db: Session, aws_account_id: int) -> Dict[str, Any]:
    # Query daily historical costs
    records = db.query(
        CostRecord.date,
        func.sum(CostRecord.amount).label('daily_total')
    ).filter(
        CostRecord.aws_account_id == aws_account_id
    ).group_by(CostRecord.date).order_by(CostRecord.date.asc()).all()

    if len(records) < 7:
        return {
            'aws_account_id': aws_account_id,
            'forecast_month': datetime.date.today().strftime('%B %Y'),
            'predicted_total': 0.0,
            'trend_percentage': 0.0,
            'model_used': 'Linear Trend Regression',
            'is_sufficient_data': False,
            'message': 'Not enough historical billing records (minimum 7 days required) to generate a reliable forecast.',
            'daily_forecasts': []
        }

    df = pd.DataFrame([{'date': r[0], 'amount': float(r[1])} for r in records])
    df['day_idx'] = np.arange(len(df))

    # Fit linear regression model on days
    X = df[['day_idx']].values
    y = df['amount'].values

    model = LinearRegression()
    model.fit(X, y)

    # Calculate standard residual error for confidence bounds
    residuals = y - model.predict(X)
    std_err = float(np.std(residuals)) if len(residuals) > 1 else 5.0

    # Project for the next 30 days
    last_day_idx = df['day_idx'].iloc[-1]
    last_date = df['date'].iloc[-1]

    future_points: List[Dict[str, Any]] = []
    future_sum = 0.0

    for i in range(1, 31):
        future_idx = last_day_idx + i
        pred_val = max(0.0, float(model.predict([[future_idx]])[0]))
        lower = max(0.0, pred_val - (1.96 * std_err))
        upper = pred_val + (1.96 * std_err)
        future_date = last_date + datetime.timedelta(days=i)

        future_points.append({
            'date': future_date.isoformat(),
            'predicted_amount': round(pred_val, 2),
            'lower_bound': round(lower, 2),
            'upper_bound': round(upper, 2)
        })
        future_sum += pred_val

    # Store forecasts in DB
    db.query(Forecast).filter(Forecast.aws_account_id == aws_account_id).delete()
    for pt in future_points:
        fc = Forecast(
            aws_account_id=aws_account_id,
            forecast_date=datetime.date.fromisoformat(pt['date']),
            predicted_amount=pt['predicted_amount'],
            lower_bound=pt['lower_bound'],
            upper_bound=pt['upper_bound'],
            model='Linear+Trend'
        )
        db.add(fc)
    db.commit()

    # Calculate trend % comparing last 14 days vs prior 14 days
    trend_pct = 0.0
    if len(df) >= 14:
        recent_mean = df['amount'].iloc[-7:].mean()
        prior_mean = df['amount'].iloc[-14:-7].mean()
        if prior_mean > 0:
            trend_pct = round(((recent_mean - prior_mean) / prior_mean) * 100, 2)

    return {
        'aws_account_id': aws_account_id,
        'forecast_month': (last_date + datetime.timedelta(days=15)).strftime('%B %Y'),
        'predicted_total': round(future_sum, 2),
        'trend_percentage': trend_pct,
        'model_used': 'Linear Trend + 95% Confidence Interval',
        'is_sufficient_data': True,
        'message': None,
        'daily_forecasts': future_points
    }
