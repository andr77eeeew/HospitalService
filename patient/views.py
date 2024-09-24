import rest_framework.generics as generics
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from patient.serializers import PatientSerializer, PatientRegisterSerializer
from users.models import User


# Create your views here.

class PatientsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = PatientSerializer
    permission_classes = (JWTAuthentication,)
    authentication_classes = (IsAuthenticated,)

    @extend_schema(description="Get patient list")
    def get_queryset(self):
        queryset = User.objects.filer(role__role='patient').related_name('role')
        return queryset


class PatientRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(role__role='patient')
    permission_classes = (AllowAny,)
    serializer_class = PatientRegisterSerializer

    @extend_schema(description="Create patient")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
