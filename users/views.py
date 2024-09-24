from smtplib import SMTPDataError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User, SubRole, ResetPassword
from users.serializers import LoginSerializer, UserSerializer, UserUpdateProfileSerializer, \
    ResetPasswordRequestSerializer, PasswordResetSerializer
from environs import Env

env = Env()
env.read_env()


class GetSubRolesView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(description="Getting the specialization that is currently in the hospital")
    def get(self, *args, **kwargs):
        doctor_role = 'doctor'

        sub_roles = SubRole.objects.filter(
            user__role__role=doctor_role
        ).distinct().values('id', 'sub_role')

        return Response({
            "sub_roles": sub_roles
        }, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    @extend_schema(description="Login user")
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
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    @extend_schema(description="Logout user")
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


class UserDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    @extend_schema(description="Get user details")
    def get(self, request, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class UserUpdateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserUpdateProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(description="Update user details")
    def get_user(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetSpecificUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    @extend_schema(description="Getting user by ID")
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = request.user
        if user.role.role == 'patient' or user.role.role == 'admin':
            user = get_object_or_404(User, id=user_id, role__role='doctor')
            serializer = self.serializer_class(user, context={'request': request})
            return Response(serializer.data)
        elif user.role.role == 'doctor' or user.role.role == 'admin':
            user = get_object_or_404(User, id=user_id, role__role='patient')
            serializer = self.serializer_class(user, context={'request': request})
            return Response(serializer.data)


class RequestPasswordReset(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = ResetPassword(email=email, token=token)
            reset.save()
            reset_link = f"{env.str('RESET_PASSWORD_URL')}/{token}"
            try:
                subject = f"Reset Password"
                html_message = render_to_string('reset_password.html', {
                    'reset_link': reset_link
                })
                message = strip_tags(html_message)
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    to=[email])
                email.attach_alternative(html_message, 'text/html')
                email.send()
            except SMTPDataError as e:
                print(e)
            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

        return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_password = data['new_password']

        reset_obj = ResetPassword.objects.filter(token=token).first()

        if not reset_obj:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(new_password)
            user.save()

            reset_obj.delete()

            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
