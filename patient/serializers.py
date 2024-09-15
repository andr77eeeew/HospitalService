from django.utils.dateparse import parse_date, parse_time

from .models import Appointment
from rest_framework import serializers
from users.models import User, Role, SubRole
from django.utils.translation import gettext as _



class PatientSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role')

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None



class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class CreateAppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role__role='patient'))
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role__role='doctor'))

    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'date', 'time', 'message')

    def create(self, validated_data):
        patient = validated_data['patient']
        doctor = validated_data['doctor']

        # Получаем строку даты и проверяем её формат
        date_str = validated_data.get('date')

        time_str = validated_data.get('time')

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date_str,
            time=time_str,
            message=validated_data.get('message', '')
        )
        return appointment