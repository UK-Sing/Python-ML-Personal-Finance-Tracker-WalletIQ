from rest_framework import serializers
from backend.insights.models import Insight


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = ('id', 'type', 'mongo_id', 'content', 'created_at')
        read_only_fields = ('id', 'mongo_id', 'content', 'created_at')
