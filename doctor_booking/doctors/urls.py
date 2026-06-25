from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('slots/add/', views.add_slot, name='add_slot'),
    path('slots/<int:slot_id>/delete/', views.delete_slot, name='delete_slot'),
    path('profile/edit/', views.edit_profile, name='edit_doctor_profile'),
]
