from django.db import models
from django.conf import settings


class Budget(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
    ]
    CATEGORY_CHOICES = [
        ('Groceries', 'Groceries'),
        ('Dining', 'Dining'),
        ('Transport', 'Transport'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Healthcare', 'Healthcare'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    limit = models.FloatField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'period')
        db_table = 'budgets_budget'
