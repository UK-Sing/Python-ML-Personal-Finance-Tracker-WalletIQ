import numpy as np
import pandas as pd
from backend.ai_engine.categorizer import CATEGORIES

_CATEGORY_COLS = [c for c in CATEGORIES if c != 'Other']


def _get_monthly_series(user_id: str) -> pd.DataFrame:
    from backend.transactions.models import Transaction
    qs = Transaction.objects.filter(user_id=int(user_id)).values('amount', 'category', 'date')
    if not qs.exists():
        return pd.DataFrame()

    df = pd.DataFrame(list(qs))
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

    pivot = (
        df.groupby(['month', 'category'])['amount']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values('month')
    )
    for cat in _CATEGORY_COLS:
        if cat not in pivot.columns:
            pivot[cat] = 0.0
    return pivot


def _linear_forecast(values: np.ndarray, n_ahead: int = 3) -> list:
    n = len(values)
    if n == 0:
        return [0.0] * n_ahead
    if n == 1:
        return [float(values[0])] * n_ahead

    x = np.arange(n)
    coeffs = np.polyfit(x, values, deg=1)
    future_x = np.arange(n, n + n_ahead)
    predictions = np.polyval(coeffs, future_x)
    return [max(0.0, round(float(v), 2)) for v in predictions]


def predict_expenses(user_id: str, n_months: int = 3) -> dict:
    pivot = _get_monthly_series(user_id)
    if pivot.empty:
        return {
            'predictions': {},
            'months_ahead': n_months,
            'status': 'no_data',
        }

    feature_cols = [c for c in _CATEGORY_COLS if c in pivot.columns]
    predictions = {}
    trend_info = {}

    for cat in feature_cols:
        values = pivot[cat].values
        forecasted = _linear_forecast(values, n_ahead=n_months)
        predictions[cat] = forecasted

        if len(values) >= 2:
            recent_avg = float(np.mean(values[-3:])) if len(values) >= 3 else float(np.mean(values))
            earlier_avg = float(np.mean(values[:-3])) if len(values) > 3 else float(values[0])
            if earlier_avg > 0:
                pct_change = ((recent_avg - earlier_avg) / earlier_avg) * 100
            else:
                pct_change = 0.0
            trend_info[cat] = {
                'direction': 'up' if pct_change > 5 else ('down' if pct_change < -5 else 'stable'),
                'pct_change': round(pct_change, 1),
            }

    total_forecast = [
        round(sum(predictions[cat][i] for cat in feature_cols), 2)
        for i in range(n_months)
    ]

    return {
        'predictions': predictions,
        'total_monthly_forecast': total_forecast,
        'trend_info': trend_info,
        'months_ahead': n_months,
        'status': 'ok',
    }
