from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, SubRole
from users.serializers import LoginSerializer, UserSerializer, UserUpdateProfileSerializer


class GetSubRolesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, *args, **kwargs):
        doctor_role='doctor'

        sub_roles = SubRole.objects.filter(
            user__role__role=doctor_role
        ).distinct().values('id', 'sub_role')

        return Response({
            "sub_roles": sub_roles
        }, status=status.HTTP_200_OK)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
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
            })
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


class UserDetailView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class UserUpdateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserUpdateProfileSerializer
    parser_classes = [MultiPartParser, FormParser]


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

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = get_object_or_404(User, id=user_id)
        serializer = self.serializer_class(user, context={'request': request})
        return Response(serializer.data)
