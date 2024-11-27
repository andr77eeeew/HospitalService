from smtplib import SMTPDataError

from datetime import timedelta
from django.utils import timezone

import rest_framework.generics as generics
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from patient.models import Appointment
from .serializers import CreateAppointmentSerializer, AppointmentSerializer


class CreateAppointmentView(generics.CreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateAppointmentSerializer

    @extend_schema(description="Create appointment")
    def perform_create(self, serializer):
        patient = self.request.user
        if patient.roles.role == 'patient':
            if serializer.is_valid(raise_exception=True):
                # Сохранение данных
                appointment = serializer.save(patient=patient)
                try:
                    subject = f"Appointment created with {appointment.doctor.first_name} {appointment.doctor.last_name}"
                    html_message = render_to_string('appointment_email.html', {
                        'patient_name': patient.first_name,
                        'doctor_name': appointment.doctor.first_name,
                        'date': appointment.date,
                        'time': appointment.time,
                    })
                    message = strip_tags(html_message)
                    email = EmailMultiAlternatives(subject, message, to=[patient.email])
                    email.send()
                except SMTPDataError as e:
                    pass
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpcomingAndRecentAppointmentsView(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AppointmentSerializer

    @extend_schema(description="Get upcoming and last three days' appointments for user")
    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        three_days_ago = now - timedelta(days=3)

        if user.roles.role == 'patient':
            # Получаем записи пациента, которые еще не прошли или произошли за последние три дня
            appointments = Appointment.objects.filter(
                patient=user, date__gte=three_days_ago
            ).order_by('date')
            return appointments
        elif user.roles.role == 'doctor':
            # Получаем записи врача, которые еще не прошли или произошли за последние три дня
            appointments = Appointment.objects.filter(
                doctor=user, date__gte=three_days_ago
            ).order_by('date')
            return appointments
        return None


class GetAppointmentForUserView(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AppointmentSerializer

    @extend_schema(description="Get appointments for user")
    def get_queryset(self):
        user = self.request.user
        if user.roles.role == 'patient':
            appointments = Appointment.objects.filter(patient=user).order_by('date')
            return appointments
        elif user.roles.role == 'doctor':
            appointments = Appointment.objects.filter(doctor=user).order_by('date')
            return appointments
        return None


class DeleteAppointmentView(generics.DestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AppointmentSerializer

    def delete(self, request, *args, **kwargs):
        # Получаем appointment_id из query параметров
        appointment_id = self.request.query_params.get('id')

        # Фильтруем по appointment_id, чтобы найти нужную запись
        instance = Appointment.objects.filter(pk=appointment_id).first()

        if not instance:
            return Response(
                {"detail": "Appointment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка прав доступа (разрешение только пациенту или доктору удалить свою запись)
        user = request.user
        if user.roles.role == 'patient' and instance.patient != user:
            return Response(
                {"detail": "You do not have permission to delete this appointment."},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user.roles.role == 'doctor' and instance.doctor != user:
            return Response(
                {"detail": "You do not have permission to delete this appointment."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Выполнение удаления
        instance.delete()

        return Response(
            {"detail": "Appointment deleted successfully."},
            status=status.HTTP_200_OK
        )
