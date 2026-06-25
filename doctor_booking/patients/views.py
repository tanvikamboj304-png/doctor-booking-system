from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from doctors.models import AvailabilitySlot, DoctorProfile


def patient_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_patient():
            messages.error(request, "Access denied: Patients only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@patient_required
def dashboard(request):
    doctors = User.objects.filter(role='doctor').select_related('doctor_profile')
    my_bookings = request.user.bookings.select_related('slot__doctor').order_by('-created_at')
    return render(request, 'patients/dashboard.html', {
        'doctors': doctors,
        'my_bookings': my_bookings,
    })


@patient_required
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role='doctor')
    profile = DoctorProfile.objects.filter(user=doctor).first()
    today = timezone.now().date()
    slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        is_booked=False,
        date__gte=today,
    ).order_by('date', 'start_time')

    # Filter to truly future slots
    now = timezone.now()
    future_slots = [s for s in slots if s.is_future()]

    return render(request, 'patients/doctor_detail.html', {
        'doctor': doctor,
        'profile': profile,
        'slots': future_slots,
    })
