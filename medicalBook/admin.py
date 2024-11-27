from django.contrib import admin

from medicalBook.models import MedicalBook


@admin.register(MedicalBook)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'patient', 'doctor', 'diagnosis', 'treatment', 'description', 'tests', 'created_at')
    list_filter = ('patient', 'diagnosis')
