import logging
from datetime import datetime

from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from doctor.serializers import DoctorSerializer, AppointmentTimesSerializer
from users.models import User
from patient.models import Appointment

# Create your views here.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class SpecialistList(APIView):

    def get(self, request, *args, **kwargs):
        if request.user.role.role != 'doctor':
            specialization = request.query_params.get('specialization')  # Используйте query_params для GET-запроса
            logger.debug("Specialization: %s", specialization)
            queryset = User.objects.filter(role__role='doctor', sub_role__sub_role=specialization)
            logger.debug("Queryset: %s", queryset)
            serializer = DoctorSerializer(queryset, many=True, context={'request': request})
            logger.debug("Serializer: %s", serializer)
            return Response(serializer.data)


class AllSpecialistList(ListAPIView):
    queryset = User.objects.filter(role__role='doctor')
    serializer_class = DoctorSerializer

    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(role__role='doctor')
        serializer = DoctorSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)



class ReturnTimeList(ListAPIView):
    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get('date')
        doctor = request.query_params.get('doctor')

        logger.debug("Received date: %s", date_str)
        logger.debug("Received doctor: %s", doctor)

        if date_str is None or doctor is None:
            logger.error("Date or doctor is missing in request parameters.")
            return Response({"error": "Date or doctor parameter is missing"}, status=400)

        date = parse_date(date_str)
        if date is None:
            logger.error("Invalid date format provided.")
            return Response({"error": "Invalid date format"}, status=400)

        TIME_CHOICES = [t[0] for t in Appointment.TIME_CHOICES]
        logger.debug("TIME_CHOICES: %s", TIME_CHOICES)

        try:
            busy_times = Appointment.objects.filter(date=date, doctor=doctor).values_list('time', flat=True)
        except Exception as e:
            logger.error("Error fetching busy times: %s", e)
            return Response({"error": "Error fetching data from the database"}, status=500)

        logger.debug("Busy times from DB: %s", busy_times)

        busy_times_set = set(busy_times)
        logger.debug("Busy times set: %s", busy_times_set)

        time_status_list = [
            {"time": t.strftime('%H:%M'), "value": t.strftime('%H:%M:%S'), "is_available": (t not in busy_times_set)}
            for t in TIME_CHOICES
        ]
        logger.debug("Time status list: %s", time_status_list)

        return Response(time_status_list)

# class BusyDates(ListAPIView):
#
#
#     def get(self, request, *args, **kwargs):
#         # Получаем все занятые часы для указанного врача на определенную дату
#         doctor = request.data.get('doctor')
#         busy_times = Appointment.objects.filter(doctor=doctor).values_list('time', flat=True)
#         # Если все доступные часы заняты, возвращаем дату
#         available_times = set(time for time, _ in Appointment._meta.get_field('time').choices)
#         if not available_times.difference(busy_times):
#             return target_date
#         return None
