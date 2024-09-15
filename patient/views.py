from django.shortcuts import render
import rest_framework.generics as generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from patient.serializers import PatientSerializer, CreateAppointmentSerializer
from users.models import User


# Create your views here.

class PatientsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        queryset = User.objects.filer(role__role='patient').related_name('role')
        return queryset


class CreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, request, *args, **kwargs):
        serailizer = self.get_serializer(data=request.data)
        if serailizer.is_valid(raise_exception=True):
            serailizer.save()
            return Response(serailizer.data, status=status.HTTP_201_CREATED)
        return Response(serailizer.errors, status=status.HTTP_400_BAD_REQUEST)
