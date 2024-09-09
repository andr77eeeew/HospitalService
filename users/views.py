from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import User
from users.serializers import PatientRegisterSerializer


class PatientRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(role__role='patient')
    permission_classes = (AllowAny,)
    serializer_class = PatientRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)