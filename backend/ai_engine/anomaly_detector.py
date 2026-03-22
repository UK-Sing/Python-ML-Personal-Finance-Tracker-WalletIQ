import numpy as np
import pandas as pd


def detect_anomalies(user_id: str, z_threshold: float = 2.0) -> dict:
    from backend.transactions.models import Transaction
    qs = Transaction.objects.filter(user_id=int(user_id)).values(
        'id', 'amount', 'category', 'description', 'date'
    )
    if not qs.exists():
        return {'anomalies': [], 'total_checked': 0, 'anomaly_count': 0}

    df = pd.DataFrame(list(qs))
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

    anomalies = []

    for category, group in df.groupby('category'):
        values = group['amount'].values
        if len(values) < 3:
            continue

        mean = float(np.mean(values))
        std = float(np.std(values))
        if std == 0:
            continue

        for _, row in group.iterrows():
            z = (row['amount'] - mean) / std
            if abs(z) > z_threshold:
                anomalies.append({
                    'transaction_id': int(row['id']),
                    'description': row.get('description', ''),
                    'amount': float(row['amount']),
                    'category': category,
                    'date': str(row.get('date', '')),
                    'z_score': round(float(z), 2),
                    'category_mean': round(mean, 2),
                    'category_std': round(std, 2),
                    'message': (
                        f"Unusually {'high' if z > 0 else 'low'} spend of "
                        f"₹{row['amount']:.2f} in {category} "
                        f"(avg ₹{mean:.2f}, z={z:.2f})"
                    ),
                })

    anomalies.sort(key=lambda x: abs(x['z_score']), reverse=True)

    return {
        'anomalies': anomalies,
        'total_checked': len(df),
        'anomaly_count': len(anomalies),
    }
