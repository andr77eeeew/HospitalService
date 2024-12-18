from datetime import timedelta, datetime, time

from django.core.mail import send_mail
from django.utils.dateparse import parse_date
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from doctor.serializers import DoctorSerializer, DoctorRegisterSerializer, DoctorUpdateSerializer
from users.models import User, SubRole
from patient.models import Appointment


class SpecialistList(APIView):

    @extend_schema(description="Get specific specialists")
    def get(self, request, *args, **kwargs):
        if request.user.roles.role != 'doctor':
            specialization = request.query_params.get('specialization')
            queryset = User.objects.filter(roles__role='doctor', sub_role__sub_role=specialization)
            serializer = DoctorSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)


class AllSpecialistList(ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = (AllowAny,)

    @extend_schema(description="Get all specialists")
    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(roles__role='doctor')
        serializer = DoctorSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class ReturnTimeList(ListAPIView):

    @extend_schema(description="Checking available hours for recording")
    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get('date')
        doctor = request.query_params.get('doctor')
        current_time = datetime.now().time()
        today = datetime.now().date()

        if date_str is None or doctor is None:
            return Response({"error": "Date or doctor parameter is missing"}, status=400)

        date = parse_date(date_str)
        if date is None:
            return Response({"error": "Invalid date format"}, status=400)

        time_choices = [t[0] for t in Appointment.TIME_CHOICES]

        try:
            busy_times = set(Appointment.objects.filter(date=date, doctor=doctor).values_list('time', flat=True))
        except Exception as e:
            return Response({"error": "Error fetching data from the database"}, status=500)

        if date == today:
            time_status_list = [
                {
                    "time": f"{t.strftime('%H:%M')}-{(datetime.combine(date.today(), t) + timedelta(minutes=50)).strftime('%H:%M')}",
                    "value": t.strftime('%H:%M:%S'),
                    "is_available": (t not in busy_times and t >= current_time)
                }
                for t in time_choices
                if
                t >= current_time and (datetime.combine(date.today(), t) + timedelta(minutes=50)) <= datetime.combine(
                    date.today(), time(23, 59))
            ]
        else:
            # Если дата не сегодня, не сравниваем с current_time
            time_status_list = [
                {
                    "time": f"{t.strftime('%H:%M')}-{(datetime.combine(date.today(), t) + timedelta(minutes=50)).strftime('%H:%M')}",
                    "value": t.strftime('%H:%M:%S'),
                    "is_available": (t not in busy_times)
                }
                for t in time_choices
                if (datetime.combine(date.today(), t) + timedelta(minutes=50)) <= datetime.combine(
                    date.today(), time(23, 59))
            ]

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


class DoctorRegisterView(CreateAPIView):
    queryset = User.objects.filter(roles__role='doctor')
    permission_classes = (IsAuthenticated,)
    serializer_class = DoctorRegisterSerializer

    @extend_schema(description="Сreate empty account for doctor")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            doctor = serializer.save()
            send_mail(
                f"Hello, {doctor.roles.role}!",
                "This is your access key for your doctor account: " + doctor.access_key,
                from_email=None,
                recipient_list=[doctor.email],
                fail_silently=False
            )
            return Response({
                "id": doctor.id,
                "role": doctor.roles.role,
                "access_key": doctor.access_key,
                "detail": "Doctor account created successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorKeyValidatorView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(description="Validate access key")
    def post(self, request, *args, **kwargs):

        access_key = request.data.get('access_key')

        if not access_key:
            return Response({"detail": "Access key is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(access_key=access_key)
        except User.DoesNotExist:
            return Response({"detail": "Invalid access key."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "detail": 'Access key is valid',
            "id": user.id,
        }, status=status.HTTP_200_OK)


class DoctorUpdateView(UpdateAPIView):
    queryset = User.objects.filter(roles__role='doctor')
    permission_classes = (AllowAny,)
    serializer_class = DoctorUpdateSerializer

    @extend_schema(description="Update doctor account")
    def update(self, request, *args, **kwargs):
        user_id = request.data.get('id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Doctor account updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
