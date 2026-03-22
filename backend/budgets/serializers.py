from rest_framework import serializers
from backend.budgets.models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    current_spend = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    overspent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            'id', 'category', 'limit', 'period',
            'current_spend', 'remaining', 'overspent', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def _get_spend(self, obj):
        from django.utils import timezone
        from backend.transactions.models import Transaction
        import django.db.models as m
        now = timezone.now()
        if obj.period == 'monthly':
            qs = Transaction.objects.filter(
                user=obj.user,
                category=obj.category,
                date__year=now.year,
                date__month=now.month,
            )
        else:
            week_start = now - timezone.timedelta(days=now.weekday())
            qs = Transaction.objects.filter(
                user=obj.user,
                category=obj.category,
                date__gte=week_start,
            )
        result = qs.aggregate(total=m.Sum('amount'))
        return result['total'] or 0.0

    def get_current_spend(self, obj):
        return round(self._get_spend(obj), 2)

    def get_remaining(self, obj):
        return round(obj.limit - self._get_spend(obj), 2)

    def get_overspent(self, obj):
        return self._get_spend(obj) > obj.limit
