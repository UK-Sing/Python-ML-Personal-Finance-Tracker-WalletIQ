from django.urls import path
from backend.budgets import views

urlpatterns = [
    path('budgets', views.budget_list, name='budget_list'),
    path('budgets/<int:pk>', views.budget_detail, name='budget_detail'),
]
