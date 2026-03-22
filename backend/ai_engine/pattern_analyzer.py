import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from backend.ai_engine.categorizer import CATEGORIES

CLUSTER_LABELS = {
    0: "Balanced Spender",
    1: "High Dining & Entertainment",
    2: "High Transport & Utilities",
    3: "Heavy Shopper",
}

_CATEGORY_COLS = [c for c in CATEGORIES if c != 'Other']


def _get_monthly_spend(user_id: str) -> pd.DataFrame:
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
    )
    for cat in _CATEGORY_COLS:
        if cat not in pivot.columns:
            pivot[cat] = 0.0
    return pivot


def analyze_patterns(user_id: str) -> dict:
    pivot = _get_monthly_spend(user_id)
    if pivot.empty or len(pivot) < 2:
        return {
            'cluster_label': 'Insufficient Data',
            'monthly_totals': {},
            'top_category': None,
            'avg_monthly_spend': 0.0,
        }

    feature_cols = [c for c in _CATEGORY_COLS if c in pivot.columns]
    X = pivot[feature_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = min(4, len(X))
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    km.fit(X_scaled)

    latest_row = X_scaled[-1].reshape(1, -1)
    cluster_id = int(km.predict(latest_row)[0])
    cluster_label = CLUSTER_LABELS.get(cluster_id, f"Cluster {cluster_id}")

    avg_spend = {cat: float(np.mean(pivot[cat])) for cat in feature_cols}
    top_category = max(avg_spend, key=avg_spend.get) if avg_spend else None
    total_monthly_avg = float(sum(avg_spend.values()))

    monthly_totals = {}
    if 'month' in pivot.columns:
        for _, row in pivot.iterrows():
            monthly_totals[row['month']] = {
                cat: round(float(row[cat]), 2) for cat in feature_cols
            }

    return {
        'cluster_label': cluster_label,
        'cluster_id': cluster_id,
        'monthly_totals': monthly_totals,
        'avg_spend_per_category': {k: round(v, 2) for k, v in avg_spend.items()},
        'top_category': top_category,
        'avg_monthly_spend': round(total_monthly_avg, 2),
    }
