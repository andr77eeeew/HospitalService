import datetime
from django.db import models
from rest_framework.exceptions import ValidationError

from users.models import User


class Appointment(models.Model):
    from datetime import time

    TIME_CHOICES = [
        (time(8, 0), '08:00 AM'),
        (time(9, 0), '09:00 AM'),
        (time(10, 0), '10:00 AM'),
        (time(11, 0), '11:00 AM'),
        (time(12, 0), '12:00 PM'),
        (time(13, 0), '01:00 PM'),
        (time(14, 0), '02:00 PM'),
        (time(15, 0), '03:00 PM'),
        (time(16, 0), '04:00 PM'),
        (time(17, 0), '05:00 PM'),
        (time(18, 0), '06:00 PM'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient',
                                limit_choices_to={'roles__role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor',
                               limit_choices_to={'roles__role': 'doctor'})
    date = models.DateField()
    time = models.TimeField(choices=TIME_CHOICES)
    end_time = models.TimeField(null=True, blank=True)
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
        if self.patient.roles.role != 'patient':
            raise ValidationError("Patient must be a patient.")

        if self.doctor.roles.role != 'doctor':
            raise ValidationError("Doctor must be a doctor.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure that validations are called before saving
        if self.time:
            start_datetime = datetime.datetime.combine(self.date, self.time)
            end_datetime = start_datetime + datetime.timedelta(hours=1)
            self.end_time = end_datetime.time()
        super().save(*args, **kwargs)
