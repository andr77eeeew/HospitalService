from django.db import models

from users.models import User


# Create your models here.
class MedicalBook(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_patient',
                                limit_choices_to={'roles__role': 'patient'}, null=True)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_doctor',
                               limit_choices_to={'roles__role': 'doctor'}, null=True)
    diagnosis = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    treatment = models.TextField(null=True, blank=True)
    tests = models.FileField(upload_to='medical_tests', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
