import logging

from django.shortcuts import render
import rest_framework.generics as generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from patient.models import Appointment
from patient.serializers import PatientSerializer, CreateAppointmentSerializer, AppointmentSerializer
from users.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Create your views here.

class PatientsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        queryset = User.objects.filer(role__role='patient').related_name('role')
        return queryset


class CreateAppointmentView(generics.CreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateAppointmentSerializer

    def perform_create(self, serializer):
        patient = self.request.user
        logger.debug(f"Request user: {patient}")
        if patient.role.role == 'patient':
            if serializer.is_valid(raise_exception=True):
                # Сохранение данных
                serializer.save(patient=patient)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAppointmentForUserView(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        patient = self.request.user
        logger.debug(f"Request user: {patient}")
        if patient.role.role == 'patient':
            appointments = Appointment.objects.filter(patient=patient)
            return appointments

        return None
