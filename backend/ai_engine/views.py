from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from backend.ai_engine.engine import run_analysis
from backend.ai_engine.categorizer import train_and_save


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze(request):
    user_id = str(request.user.id)
    try:
        summary = run_analysis(user_id)
        return Response({'status': 'ok', 'summary': summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retrain_categorizer(request):
    try:
        train_and_save()
        return Response({'status': 'categorizer retrained successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
