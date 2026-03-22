import pandas as pd
from django.utils import timezone


def _get_current_month_spend(user_id: str) -> dict:
    from backend.transactions.models import Transaction
    now = timezone.now()
    qs = Transaction.objects.filter(
        user_id=int(user_id),
        date__year=now.year,
        date__month=now.month,
    ).values('category', 'amount')
    if not qs.exists():
        return {}
    df = pd.DataFrame(list(qs))
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    return df.groupby('category')['amount'].sum().to_dict()


def _get_budgets(user_id: str) -> dict:
    from backend.budgets.models import Budget
    qs = Budget.objects.filter(user_id=int(user_id)).values('category', 'limit')
    return {b['category']: float(b['limit']) for b in qs}


def _get_all_spend(user_id: str) -> pd.DataFrame:
    from backend.transactions.models import Transaction
    qs = Transaction.objects.filter(user_id=int(user_id)).values('amount', 'category', 'date')
    if not qs.exists():
        return pd.DataFrame()
    df = pd.DataFrame(list(qs))
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    return df


def generate_recommendations(user_id: str) -> list:
    recommendations = []
    current_spend = _get_current_month_spend(user_id)
    budgets = _get_budgets(user_id)
    df = _get_all_spend(user_id)

    for category, limit in budgets.items():
        spent = current_spend.get(category, 0.0)
        if limit > 0:
            pct = (spent / limit) * 100
            if pct >= 100:
                recommendations.append({
                    'type': 'budget_exceeded',
                    'severity': 'high',
                    'category': category,
                    'message': (
                        f"You have exceeded your {category} budget! "
                        f"Spent ₹{spent:.2f} vs limit ₹{limit:.2f} ({pct:.0f}%)."
                    ),
                })
            elif pct >= 80:
                recommendations.append({
                    'type': 'budget_warning',
                    'severity': 'medium',
                    'category': category,
                    'message': (
                        f"You are at {pct:.0f}% of your {category} budget. "
                        f"₹{limit - spent:.2f} remaining this month."
                    ),
                })

    if not df.empty and 'month' in df.columns:
        pivot = (
            df.groupby(['month', 'category'])['amount']
            .sum()
            .unstack(fill_value=0)
            .sort_index()
        )
        for cat in pivot.columns:
            values = pivot[cat].values
            if len(values) >= 3:
                recent = float(values[-1])
                prior_avg = float(values[:-1].mean())
                if prior_avg > 0 and recent > prior_avg * 1.3:
                    recommendations.append({
                        'type': 'spending_spike',
                        'severity': 'medium',
                        'category': cat,
                        'message': (
                            f"Your {cat} spending spiked by "
                            f"{((recent - prior_avg) / prior_avg * 100):.0f}% "
                            f"compared to your usual average."
                        ),
                    })

    if not df.empty:
        total_spend = float(df['amount'].sum())
        months = df['month'].nunique() if 'month' in df.columns else 1
        avg_monthly = total_spend / max(months, 1)
        potential_savings = avg_monthly * 0.10
        recommendations.append({
            'type': 'savings_opportunity',
            'severity': 'low',
            'category': None,
            'message': (
                f"Your average monthly spend is ₹{avg_monthly:.2f}. "
                f"Cutting discretionary spending by 10% could save "
                f"₹{potential_savings:.2f}/month."
            ),
        })

    if not recommendations:
        recommendations.append({
            'type': 'healthy_finances',
            'severity': 'low',
            'category': None,
            'message': "Your finances look healthy! Keep tracking to get personalized tips.",
        })

    return recommendations
