import json
from datetime import datetime, timezone
from backend.ai_engine.pattern_analyzer import analyze_patterns
from backend.ai_engine.predictor import predict_expenses
from backend.ai_engine.anomaly_detector import detect_anomalies
from backend.ai_engine.recommender import generate_recommendations


def _try_mongo_insert(user_id: str, insight_type: str, content: dict, now: str) -> str:
    try:
        from backend.db_client import get_collection
        result = get_collection('insights').insert_one({
            'user_id': user_id,
            'type': insight_type,
            'content': content,
            'created_at': now,
        })
        return str(result.inserted_id)
    except Exception:
        return ''


def run_analysis(user_id: str) -> dict:
    from backend.insights.models import Insight

    pattern_result = analyze_patterns(user_id)
    prediction_result = predict_expenses(user_id)
    anomaly_result = detect_anomalies(user_id)
    recommendations = generate_recommendations(user_id)

    now = datetime.now(timezone.utc).isoformat()

    insight_types = [
        ('spending_pattern', pattern_result),
        ('expense_prediction', prediction_result),
        ('anomaly_detection', anomaly_result),
        ('recommendations', {'items': recommendations}),
    ]

    created_ids = []
    for insight_type, content in insight_types:
        mongo_id = _try_mongo_insert(user_id, insight_type, content, now)
        created_ids.append(mongo_id or insight_type)
        Insight.objects.create(
            user_id=int(user_id),
            type=insight_type,
            mongo_id=mongo_id,
            content=content,
        )

    summary = {
        'insight_ids': created_ids,
        'spending_pattern': {
            'cluster_label': pattern_result.get('cluster_label'),
            'top_category': pattern_result.get('top_category'),
            'avg_monthly_spend': pattern_result.get('avg_monthly_spend'),
        },
        'predictions': {
            'total_monthly_forecast': prediction_result.get('total_monthly_forecast', []),
            'status': prediction_result.get('status'),
        },
        'anomalies': {
            'count': anomaly_result.get('anomaly_count', 0),
            'top': anomaly_result.get('anomalies', [])[:3],
        },
        'recommendations_count': len(recommendations),
        'analyzed_at': now,
    }
    return summary
