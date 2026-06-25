from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from doctors.models import AvailabilitySlot
from .models import Booking


def patient_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_patient():
            messages.error(request, "Access denied: Patients only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@patient_required
def book_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)

    if not slot.is_future():
        messages.error(request, "This slot is in the past.")
        return redirect('patient_dashboard')

    if slot.is_booked:
        messages.error(request, "This slot has already been booked.")
        return redirect('patient_dashboard')

    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        try:
            with transaction.atomic():
                # Lock the slot row to prevent race conditions
                locked_slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
                if locked_slot.is_booked:
                    messages.error(request, "Sorry, this slot was just booked by someone else.")
                    return redirect('patient_dashboard')

                booking = Booking.objects.create(
                    patient=request.user,
                    slot=locked_slot,
                    notes=notes,
                )
                locked_slot.is_booked = True
                locked_slot.save()

            # Send confirmation emails (non-blocking, outside transaction)
            try:
                send_mail(
                    subject='Booking Confirmed',
                    message=(
                        f"Dear {request.user.first_name or request.user.username},\n\n"
                        f"Your appointment with {locked_slot.doctor.get_full_name() or locked_slot.doctor.username} "
                        f"on {locked_slot.date} at {locked_slot.start_time} has been confirmed.\n\n"
                        f"Thank you!"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
                send_mail(
                    subject='New Appointment Booked',
                    message=(
                        f"Dear Dr. {locked_slot.doctor.get_full_name() or locked_slot.doctor.username},\n\n"
                        f"Patient {request.user.get_full_name() or request.user.email} has booked your slot "
                        f"on {locked_slot.date} at {locked_slot.start_time}.\n\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[locked_slot.doctor.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, "Appointment booked successfully! A confirmation email has been sent.")
            return redirect('patient_dashboard')

        except IntegrityError:
            messages.error(request, "Sorry, this slot was just booked by someone else.")
            return redirect('patient_dashboard')

    return render(request, 'bookings/confirm_booking.html', {'slot': slot})


@patient_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, patient=request.user)
    if request.method == 'POST':
        slot = booking.slot
        slot.is_booked = False
        slot.save()
        booking.delete()
        messages.success(request, "Booking cancelled.")
    return redirect('patient_dashboard')


@login_required
def my_bookings(request):
    if request.user.is_patient():
        bookings = Booking.objects.filter(patient=request.user).select_related('slot__doctor')
    else:
        bookings = Booking.objects.filter(slot__doctor=request.user).select_related('patient', 'slot')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})
