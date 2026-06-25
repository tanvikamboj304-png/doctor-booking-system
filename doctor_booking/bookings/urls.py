from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
]
