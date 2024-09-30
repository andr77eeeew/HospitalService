import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ChatRoom


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
