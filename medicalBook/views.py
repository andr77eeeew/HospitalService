from datetime import date, datetime

from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from medicalBook.models import MedicalBook
from medicalBook.seralizers import CreateMedicalBookSerializer, MedicalBookSerializer
from patient.models import Appointment


class CreateMedicalBookView(CreateAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = CreateMedicalBookSerializer

    def get(self, request, *args, **kwargs):
        doctor_id = self.request.user
        patient_id = request.query_params.get('patient_id')

        appointments = Appointment.objects.filter(patient=patient_id, doctor=doctor_id, date=date.today())

        now = datetime.now()

        can_create = False
        for appointment in appointments:
            if appointment.time <= now.time() <= appointment.end_time:
                can_create = True
                break

        if can_create:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        doctor = self.request.user
        if doctor.role.role == 'doctor':
            if serializer.is_valid(raise_exception=True):
                # Сохранение данных
                medicalbook = serializer.save(doctor=doctor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMedicalBookView(ListAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated,)
    serializer_class = MedicalBookSerializer

    def get_queryset(self):
        patient = self.request.user
        if patient.role.role == 'patient':
            medicalbooks = MedicalBook.objects.filter(patient=patient)
            return medicalbooks
