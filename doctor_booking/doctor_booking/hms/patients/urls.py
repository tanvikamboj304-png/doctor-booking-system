from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='patient_dashboard'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
]
