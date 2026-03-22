from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from backend.budgets.models import Budget
from backend.budgets.serializers import BudgetSerializer
from backend.db_client import get_collection


def _sync_to_mongo(budget: Budget):
    col = get_collection('budgets')
    doc = {
        'django_id': budget.id,
        'user_id': str(budget.user_id),
        'category': budget.category,
        'limit': budget.limit,
        'period': budget.period,
    }
    col.update_one({'django_id': budget.id}, {'$set': doc}, upsert=True)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def budget_list(request):
    if request.method == 'GET':
        budgets = Budget.objects.filter(user=request.user)
        return Response(BudgetSerializer(budgets, many=True).data)

    serializer = BudgetSerializer(data=request.data)
    if serializer.is_valid():
        budget = serializer.save(user=request.user)
        _sync_to_mongo(budget)
        return Response(BudgetSerializer(budget).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def budget_detail(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'GET':
        return Response(BudgetSerializer(budget).data)

    if request.method == 'PUT':
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            budget = serializer.save()
            _sync_to_mongo(budget)
            return Response(BudgetSerializer(budget).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    get_collection('budgets').delete_one({'django_id': budget.id})
    budget.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
