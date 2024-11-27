from datetime import date, datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
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

    @extend_schema(description="Check if doctor can create medical book")
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

    @extend_schema(description="Create medical book")
    def perform_create(self, serializer):
        doctor = self.request.user
        if doctor.roles.role == 'doctor':
            if serializer.is_valid(raise_exception=True):
                # Сохранение данных
                medicalbook = serializer.save(doctor=doctor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMedicalBooksView(ListAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated,)
    serializer_class = MedicalBookSerializer

    @extend_schema(description="Get medical books")
    def get_queryset(self):
        patient = self.request.user
        if patient.roles.role == 'patient':
            medicalbooks = MedicalBook.objects.filter(patient=patient)
            return medicalbooks


class GetMedicalBookView(ListAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = (IsAuthenticated,)
    serializer_class = MedicalBookSerializer

    @extend_schema(description="Get medical book")
    def get_queryset(self):
        patient = self.request.user
        id = self.request.query_params.get('id')
        if patient.roles.role == 'patient':
            medicalbooks = MedicalBook.objects.filter(patient=patient, id=id)
            return medicalbooks
