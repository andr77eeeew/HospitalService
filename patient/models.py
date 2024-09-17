import datetime
from django.db import models
from rest_framework.exceptions import ValidationError

from users.models import User


class Appointment(models.Model):
    TIME_CHOICES = [
        (datetime.time(9, 0), '09:00 AM'),
        (datetime.time(10, 0), '10:00 AM'),
        (datetime.time(11, 0), '11:00 AM'),
        (datetime.time(12, 0), '12:00 PM'),
        (datetime.time(13, 0), '01:00 PM'),
        (datetime.time(14, 0), '02:00 PM'),
        (datetime.time(15, 0), '03:00 PM'),
        (datetime.time(16, 0), '04:00 PM'),
        (datetime.time(17, 0), '05:00 PM'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient',
                                limit_choices_to={'role__role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor',
                               limit_choices_to={'role__role': 'doctor'})
    date = models.DateField()
    time = models.TimeField(choices=TIME_CHOICES)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Проверка даты
        if self.date < datetime.date.today():
            raise ValidationError("Date cannot be in the past.")

        # Проверка времени
        now = datetime.datetime.now()
        appointment_datetime = datetime.datetime.combine(self.date, self.time)
        if appointment_datetime < now:
            raise ValidationError("Date and time cannot be in the past.")

        # Проверка ролей
        if self.patient.role.role != 'patient':
            raise ValidationError("Patient must be a patient.")

        if self.doctor.role.role != 'doctor':
            raise ValidationError("Doctor must be a doctor.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure that validations are called before saving
        super().save(*args, **kwargs)

