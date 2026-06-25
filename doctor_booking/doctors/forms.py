from django import forms
from .models import AvailabilitySlot, DoctorProfile
from django.utils import timezone


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if date and date < timezone.now().date():
            raise forms.ValidationError("Slot date cannot be in the past.")

        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data
