from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from backend.transactions.models import Transaction
from backend.transactions.serializers import TransactionSerializer
from backend.ai_engine.categorizer import predict_category
from backend.db_client import get_collection


def _sync_to_mongo(transaction: Transaction):
    try:
        col = get_collection('transactions')
        doc = {
            'django_id': transaction.id,
            'user_id': str(transaction.user_id),
            'amount': transaction.amount,
            'category': transaction.category,
            'description': transaction.description,
            'date': transaction.date.isoformat(),
            'auto_categorized': transaction.auto_categorized,
        }
        col.update_one({'django_id': transaction.id}, {'$set': doc}, upsert=True)
    except Exception:
        return


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        qs = Transaction.objects.filter(user=request.user)
        if category:
            qs = qs.filter(category=category)
        return Response(TransactionSerializer(qs, many=True).data)

    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        description = serializer.validated_data.get('description', '')
        category = serializer.validated_data.get('category', 'Other')
        auto_cat = False
        if description and category == 'Other':
            try:
                category = predict_category(description)
                auto_cat = True
            except Exception:
                pass
        tx = serializer.save(user=request.user, category=category, auto_categorized=auto_cat)
        _sync_to_mongo(tx)
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'GET':
        return Response(TransactionSerializer(tx).data)

    if request.method == 'PUT':
        serializer = TransactionSerializer(tx, data=request.data, partial=True)
        if serializer.is_valid():
            tx = serializer.save()
            _sync_to_mongo(tx)
            return Response(TransactionSerializer(tx).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        get_collection('transactions').delete_one({'django_id': tx.id})
    except Exception:
        pass
    tx.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_summary(request):
    from django.db.models import Sum, Count
    qs = Transaction.objects.filter(user=request.user)
    summary = (
        qs.values('category')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    total_spend = sum(item['total'] for item in summary)
    return Response({
        'by_category': list(summary),
        'total_spend': round(total_spend, 2),
        'transaction_count': qs.count(),
    })
