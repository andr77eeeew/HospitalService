import rest_framework.generics as generics
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

    def perform_create(self, serializer):
        patient = self.request.user
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
        if patient.role.role == 'patient':
            appointments = Appointment.objects.filter(patient=patient)
            return appointments

        return None
