from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import AvailabilitySlot, DoctorProfile
from .forms import AvailabilitySlotForm, DoctorProfileForm
from bookings.models import Booking


def doctor_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_doctor():
            messages.error(request, "Access denied: Doctors only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@doctor_required
def dashboard(request):
    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('date', 'start_time')
    bookings = Booking.objects.filter(slot__doctor=request.user).select_related('patient', 'slot').order_by('-created_at')
    profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    return render(request, 'doctors/dashboard.html', {
        'slots': slots,
        'bookings': bookings,
        'profile': profile,
        'today': timezone.now().date(),
    })


@doctor_required
def add_slot(request):
    form = AvailabilitySlotForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        slot = form.save(commit=False)
        slot.doctor = request.user
        # Check for overlapping slots
        existing = AvailabilitySlot.objects.filter(
            doctor=request.user,
            date=slot.date,
            start_time=slot.start_time
        ).exists()
        if existing:
            messages.error(request, "You already have a slot at this time.")
        else:
            slot.save()
            messages.success(request, "Availability slot added.")
            return redirect('doctor_dashboard')
    return render(request, 'doctors/add_slot.html', {'form': form})


@doctor_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user)
    if slot.is_booked:
        messages.error(request, "Cannot delete a booked slot.")
    else:
        slot.delete()
        messages.success(request, "Slot deleted.")
    return redirect('doctor_dashboard')


@doctor_required
def edit_profile(request):
    profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    form = DoctorProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect('doctor_dashboard')
    return render(request, 'doctors/edit_profile.html', {'form': form})
