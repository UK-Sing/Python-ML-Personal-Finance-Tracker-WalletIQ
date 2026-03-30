import re

# ---------------------------------------------------------------------------
# 1.  Curated small-talk dictionary — exact and substring keyword matching.
#     No external corpus. Only finance-contextual responses.
# ---------------------------------------------------------------------------

_SMALL_TALK: list[tuple[list[str], str]] = [
    (
        ['hello', 'hi', 'hey', 'howdy', 'good morning', 'good afternoon', 'good evening'],
        "Hi! I'm your WalletIQ AI Coach. Ask me about your spending, budgets, predictions, or anomalies.",
    ),
    (
        ['thank you', 'thanks', 'cheers', 'thx'],
        "You're welcome! Let me know if you need more financial insights.",
    ),
    (
        ['bye', 'goodbye', 'see you', 'cya', 'ttyl'],
        "Goodbye! Keep tracking your spending for better financial health.",
    ),
    (
        ['help', 'what can you do', 'capabilities', 'options'],
        (
            "I can help you with:\n"
            "  • Spending summaries — \"How much did I spend on Groceries?\"\n"
            "  • Budget status      — \"Am I over budget?\"\n"
            "  • Anomaly detection  — \"Any unusual transactions?\"\n"
            "  • Expense forecast   — \"Predict my spending next month\"\n"
            "  • Recommendations    — \"Give me saving tips\""
        ),
    ),
    (
        ['who are you', 'what are you', 'tell me about yourself'],
        "I'm the WalletIQ AI Coach — a rule-based financial assistant that analyses your spending, tracks budgets, and surfaces ML-powered insights.",
    ),
    (
        ['how are you', 'how do you do'],
        "I'm running great! Ready to help you take control of your finances.",
    ),
    (
        ['ok', 'okay', 'alright', 'got it', 'understood', 'cool', 'great', 'nice'],
        "Let me know if there's anything else I can help you with!",
    ),
]


def _small_talk_reply(text: str) -> str | None:
    """Return a curated response if the input matches a small-talk keyword."""
    lower = text.lower().strip()
    for keywords, response in _SMALL_TALK:
        for kw in keywords:
            if lower == kw or lower.startswith(kw + ' ') or lower.endswith(' ' + kw):
                return response
    return None


# ---------------------------------------------------------------------------
# 2.  Finance intent parser — keyword / regex rules that route to the
#     existing AI modules (spending summary, budgets, anomalies, etc.).
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ('spending_summary', [
        r'how much.*(spend|spent)',
        r'(spend|spending).*(summar|total|breakdown|categor)',
        r'(top|biggest|highest|most).*(spend|categor|expense)',
        r'categor.*(breakdown|split|wise)',
        r'where.*(money|spend|going)',
    ]),
    ('budget_status', [
        r'(am i|are we).*(over|under|within).*(budget)',
        r'budget.*(status|check|left|remain|how)',
        r'over\s*budget',
        r'under\s*budget',
        r'(how|what).*(budget)',
    ]),
    ('anomalies', [
        r'anomal',
        r'unusual.*(spend|transaction|expense)',
        r'weird.*(spend|transaction|charge)',
        r'suspicious.*(spend|transaction)',
        r'outlier',
        r'flag.*(transaction|spend)',
    ]),
    ('predictions', [
        r'predict',
        r'forecast',
        r'next month',
        r'future.*(spend|expense)',
        r'(will|going to).*(spend|cost)',
        r'expect.*(spend|expense)',
    ]),
    ('recommendations', [
        r'recommend',
        r'advice',
        r'suggest',
        r'(how|tips).*(save|saving|cut|reduce)',
        r'(help|give).*(tip|advice|suggest|recommend)',
        r'what should i do',
        r'improve.*(financ|spend|budget)',
    ]),
]


def _detect_intent(text: str) -> str | None:
    lower = text.lower()
    for intent, patterns in _INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, lower):
                return intent
    return None


def _extract_category(text: str) -> str | None:
    from backend.ai_engine.categorizer import CATEGORIES
    lower = text.lower()
    for cat in CATEGORIES:
        if cat.lower() in lower:
            return cat
    return None


# ---------------------------------------------------------------------------
# 3.  Intent handlers — call existing AI modules and format responses.
# ---------------------------------------------------------------------------

def _handle_spending_summary(user_id: str, text: str) -> str:
    from backend.transactions.models import Transaction
    from django.db.models import Sum, Count

    category = _extract_category(text)
    qs = Transaction.objects.filter(user_id=int(user_id))

    if category:
        qs = qs.filter(category=category)
        agg = qs.aggregate(total=Sum('amount'), count=Count('id'))
        total = agg['total'] or 0
        count = agg['count'] or 0
        return (
            f"You've spent ₹{total:,.2f} on {category} "
            f"across {count} transaction{'s' if count != 1 else ''}."
        )

    summary = (
        qs.values('category')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    if not summary:
        return "You don't have any transactions yet. Add some to get insights!"

    lines = [f"Here's your spending breakdown:"]
    grand_total = 0.0
    for row in summary:
        lines.append(f"  • {row['category']}: ₹{row['total']:,.2f} ({row['count']} txns)")
        grand_total += row['total']
    lines.append(f"  Total: ₹{grand_total:,.2f}")
    return "\n".join(lines)


def _handle_budget_status(user_id: str, text: str) -> str:
    from backend.budgets.models import Budget
    from backend.transactions.models import Transaction
    from django.db.models import Sum
    from django.utils import timezone

    now = timezone.now()
    budgets = Budget.objects.filter(user_id=int(user_id))
    if not budgets.exists():
        return "You haven't set any budgets yet. Create budgets to track your spending limits!"

    lines = ["Here's your budget status this month:"]
    any_over = False
    for b in budgets:
        spent_agg = Transaction.objects.filter(
            user_id=int(user_id),
            category=b.category,
            date__year=now.year,
            date__month=now.month,
        ).aggregate(total=Sum('amount'))
        spent = spent_agg['total'] or 0
        pct = (spent / b.limit * 100) if b.limit > 0 else 0
        remaining = b.limit - spent
        status_emoji = "✅" if pct < 80 else ("⚠️" if pct < 100 else "🚨")
        lines.append(
            f"  {status_emoji} {b.category}: ₹{spent:,.2f} / ₹{b.limit:,.2f} "
            f"({pct:.0f}%) — ₹{remaining:,.2f} remaining"
        )
        if pct >= 100:
            any_over = True

    if any_over:
        lines.append("\n⚠️ You've exceeded one or more budgets! Consider cutting back.")
    else:
        lines.append("\n👍 You're within all your budgets. Keep it up!")
    return "\n".join(lines)


def _handle_anomalies(user_id: str, text: str) -> str:
    from backend.ai_engine.anomaly_detector import detect_anomalies
    result = detect_anomalies(user_id)
    count = result.get('anomaly_count', 0)
    if count == 0:
        return "No anomalies detected in your transactions. Everything looks normal!"

    lines = [f"I found {count} unusual transaction{'s' if count != 1 else ''}:"]
    for a in result['anomalies'][:5]:
        lines.append(f"  🔴 {a['message']}")
    if count > 5:
        lines.append(f"  ... and {count - 5} more.")
    return "\n".join(lines)


def _handle_predictions(user_id: str, text: str) -> str:
    from backend.ai_engine.predictor import predict_expenses
    result = predict_expenses(user_id)
    if result.get('status') == 'no_data':
        return "I need more transaction history to make predictions. Keep logging your expenses!"

    forecasts = result.get('total_monthly_forecast', [])
    predictions = result.get('predictions', {})
    trend_info = result.get('trend_info', {})

    lines = ["Here's your 3-month expense forecast:"]
    for i, total in enumerate(forecasts, 1):
        lines.append(f"  Month {i}: ₹{total:,.2f}")

    if trend_info:
        lines.append("\nCategory trends:")
        for cat, info in trend_info.items():
            arrow = "📈" if info['direction'] == 'up' else ("📉" if info['direction'] == 'down' else "➡️")
            lines.append(f"  {arrow} {cat}: {info['direction']} ({info['pct_change']:+.1f}%)")

    return "\n".join(lines)


def _handle_recommendations(user_id: str, text: str) -> str:
    from backend.ai_engine.recommender import generate_recommendations
    recs = generate_recommendations(user_id)
    if not recs:
        return "No specific recommendations right now. Your finances look healthy!"

    lines = ["Here are my recommendations:"]
    for r in recs:
        severity_icon = {"high": "🚨", "medium": "⚠️", "low": "💡"}.get(r['severity'], "•")
        lines.append(f"  {severity_icon} {r['message']}")
    return "\n".join(lines)


_INTENT_HANDLERS = {
    'spending_summary': _handle_spending_summary,
    'budget_status': _handle_budget_status,
    'anomalies': _handle_anomalies,
    'predictions': _handle_predictions,
    'recommendations': _handle_recommendations,
}

FALLBACK_MESSAGE = (
    "I'm not sure I understand. I can help with:\n"
    "  • Spending summaries — \"How much did I spend on Groceries?\"\n"
    "  • Budget status — \"Am I over budget?\"\n"
    "  • Anomaly detection — \"Any anomalies?\"\n"
    "  • Predictions — \"Predict next month\"\n"
    "  • Recommendations — \"Give me advice\"\n"
    "Try asking one of these!"
)


# ---------------------------------------------------------------------------
# 4.  Public API — single entry point for the chat endpoint.
# ---------------------------------------------------------------------------

def get_chat_response(user_id: str, message: str) -> dict:
    """Process a user chat message and return a response dict.

    Priority order:
      1. Finance intent  → route to existing AI modules
      2. Small-talk      → curated keyword-matched responses
      3. Fallback        → help text listing available commands
    """
    text = message.strip()
    if not text:
        return {'response': "Please type a message and I'll do my best to help!", 'intent': None}

    # 1. Finance intent
    intent = _detect_intent(text)
    if intent and intent in _INTENT_HANDLERS:
        try:
            response = _INTENT_HANDLERS[intent](user_id, text)
            return {'response': response, 'intent': intent}
        except Exception as e:
            return {
                'response': f"I encountered an error while processing that: {e}",
                'intent': intent,
            }

    # 2. Curated small-talk
    small_talk = _small_talk_reply(text)
    if small_talk:
        return {'response': small_talk, 'intent': 'general'}

    # 3. Fallback
    return {'response': FALLBACK_MESSAGE, 'intent': None}
