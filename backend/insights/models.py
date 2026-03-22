from django.db import models
from django.conf import settings


class Insight(models.Model):
    TYPE_CHOICES = [
        ('spending_pattern', 'Spending Pattern'),
        ('expense_prediction', 'Expense Prediction'),
        ('anomaly_detection', 'Anomaly Detection'),
        ('recommendations', 'Recommendations'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='insights',
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    mongo_id = models.CharField(max_length=50, blank=True, default='')
    content = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'insights_insight'
