from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from backend.insights.models import Insight
from backend.insights.serializers import InsightSerializer
from backend.db_client import get_collection


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def insight_list(request):
    insight_type = request.query_params.get('type')
    qs = Insight.objects.filter(user=request.user)
    if insight_type:
        qs = qs.filter(type=insight_type)
    return Response(InsightSerializer(qs, many=True).data)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def insight_detail(request, pk):
    insight = get_object_or_404(Insight, pk=pk, user=request.user)

    if request.method == 'GET':
        return Response(InsightSerializer(insight).data)

    if insight.mongo_id:
        try:
            from bson import ObjectId
            get_collection('insights').delete_one({'_id': ObjectId(insight.mongo_id)})
        except Exception:
            pass
    insight.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
