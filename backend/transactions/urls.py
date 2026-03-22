from django.urls import path
from backend.transactions import views

urlpatterns = [
    path('transactions', views.transaction_list, name='transaction_list'),
    path('transactions/<int:pk>', views.transaction_detail, name='transaction_detail'),
    path('transactions/summary', views.transaction_summary, name='transaction_summary'),
]
