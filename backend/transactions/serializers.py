from rest_framework import serializers
from backend.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'amount', 'category', 'description',
            'date', 'auto_categorized', 'created_at',
        )
        read_only_fields = ('id', 'auto_categorized', 'created_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive.')
        return value
