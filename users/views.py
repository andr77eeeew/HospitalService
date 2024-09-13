from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

from users.models import User, SubRole
from users.serializers import PatientRegisterSerializer, PatientLoginSerializer, UserSerializer, \
    DoctorRegisterSerializer, DoctorUpdateSerializer


class PatientRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(role__role='patient')
    permission_classes = (AllowAny,)
    serializer_class = PatientRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorRegisterView(generics.CreateAPIView):
    queryset = User.objects.filter(role__role='doctor')
    permission_classes = (IsAuthenticated,)
    serializer_class = DoctorRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            doctor = serializer.save()
            send_mail(
                f"Hello, {doctor.role.role}!",
                "This is your access key for your doctor account: " + doctor.access_key,
                from_email=None,
                recipient_list=[doctor.email],
                fail_silently=False
            )
            return Response({
                "id": doctor.id,
                "role": doctor.role.role,
                "access_key": doctor.access_key,
                "detail": "Doctor account created successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorKeyValidatorView(APIView):
    permission_classes = (AllowAny,)

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


class GetSubRolesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        sub_roles = SubRole.objects.all().values('id', 'sub_role')
        return Response({
            "sub_roles": sub_roles
        }, status=status.HTTP_200_OK)


class DoctorUpdateView(generics.UpdateAPIView):
    queryset = User.objects.filter(role__role='doctor')
    permission_classes = (AllowAny,)
    serializer_class = DoctorUpdateSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем сериализатор для обновления существующего объекта
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Doctor account updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = PatientLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": user.email,
                "role": user.role.role,
                "Admin": user.is_staff,
                "refreshToken": str(refresh),
                "accessToken": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        access_token = request.headers.get('Authorization')
        if not access_token:
            return Response({"detail": "Access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required in the payload."}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response


class PatientsList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filer(role__role='patient').related_name('role', 'sub_role')
        return queryset


class DoctorList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filer(role__role='doctor').related_name('role', 'sub_role')
        return queryset


class UserDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
