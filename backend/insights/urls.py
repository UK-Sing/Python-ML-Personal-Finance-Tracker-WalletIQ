from django.urls import path
from backend.insights import views

urlpatterns = [
    path('insights', views.insight_list, name='insight_list'),
    path('insights/<int:pk>', views.insight_detail, name='insight_detail'),
]
