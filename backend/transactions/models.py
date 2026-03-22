from django.db import models
from django.conf import settings


class Transaction(models.Model):
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
        related_name='transactions',
    )
    amount = models.FloatField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField(blank=True, default='')
    date = models.DateTimeField()
    auto_categorized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        db_table = 'transactions_transaction'
