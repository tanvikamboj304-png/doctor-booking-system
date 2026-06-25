from django.db import models
from accounts.models import User
from django.utils import timezone


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def is_future(self):
        now = timezone.now()
        slot_dt = timezone.datetime.combine(self.date, self.start_time)
        slot_dt = timezone.make_aware(slot_dt)
        return slot_dt > now

    def __str__(self):
        return f"{self.doctor} — {self.date} {self.start_time}–{self.end_time}"
