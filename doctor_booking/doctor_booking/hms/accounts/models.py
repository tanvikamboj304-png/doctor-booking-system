from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'
    ROLE_CHOICES = [
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    def __str__(self):
        return f"{self.email} ({self.role})"
