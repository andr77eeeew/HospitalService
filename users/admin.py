from django.contrib import admin

from patient.models import Appointment
from .models import User, Role, SubRole


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role', 'sub_role', 'password',)
    list_filter = ('role', 'gender')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role',)


@admin.register(SubRole)
class SubRoleAdmin(admin.ModelAdmin):
    list_display = ('main_role', 'sub_role')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'message', 'created_at')
    list_filter = ('doctor', 'patient', 'date')
