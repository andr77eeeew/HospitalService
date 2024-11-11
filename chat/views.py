import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ChatRoom
from .serializers import ChatRoomSerializer


class ChatRoomView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        if request.user.role.role == 'doctor':
            doctor = request.user.id
            patient = request.data.get('user_id')
        elif request.user.role.role == 'patient':
            doctor = request.data.get('user_id')
            patient = request.user.id
        else:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            room = ChatRoom.objects.get(doctor_id=doctor, patient_id=patient)
            return Response({'room_name': room.name}, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            uuid_str = str(uuid.uuid4())
            room_name = f'Room_{doctor}_{patient}_{uuid_str}'  # Название новой комнаты
            room = ChatRoom.objects.create(name=room_name, doctor_id=doctor, patient_id=patient)

            return Response({'room_name': room.name}, status=status.HTTP_201_CREATED)


class RecentlyChat(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        if user.role.role == 'doctor':
            queryset = ChatRoom.objects.filter(doctor=user)
        elif user.role.role == 'patient':
            queryset = ChatRoom.objects.filter(patient=user)
        else:
            queryset = []

        serializer = ChatRoomSerializer(queryset, many=True, context={'request_user': user, 'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
