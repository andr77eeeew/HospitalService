from datetime import datetime

from .models import Appointment
from rest_framework import serializers
from users.models import User



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
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'date', 'time', 'message', 'created_at', 'doctor_id', 'patient_name', 'doctor_name')

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}"

    def doctor_id(self, obj):
        return obj.doctor.id

class CreateAppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role__role='doctor'))
    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'date', 'time', 'message')
        extra_kwargs = {
            'patient': {'required': False},
            'doctor': {'required': True},
        }

    def create(self, validated_data):
        doctor = validated_data['doctor']
        request = self.context.get('request')
        patient = request.user if request else None

        if not patient or patient.role.role != 'patient':
            raise serializers.ValidationError("You are not a patient")

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