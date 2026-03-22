from django.urls import path
from backend.ai_engine import views

urlpatterns = [
    path('ai/analyze', views.analyze, name='ai_analyze'),
    path('ai/retrain', views.retrain_categorizer, name='ai_retrain'),
]
