from rest_framework import serializers
from .models import ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='name')
    user_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['room_name', 'user_name', 'user_id', 'avatar']

    def get_user_name(self, obj):
        request_user = self.context['request_user']
        if request_user.role.role == 'doctor':
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        elif request_user.role.role == 'patient':
            return f"{obj.doctor.first_name} {obj.doctor.last_name}"
        return None

    def get_user_id(self, obj):
        request_user = self.context['request_user']
        if request_user.role.role == 'doctor':
            return obj.patient.id
        elif request_user.role.role == 'patient':
            return obj.doctor.id
        return None

    def get_avatar(self, obj):
        request = self.context.get('request')
        request_user = self.context['request_user']

        # Depending on the role, fetch the patient's or doctor's avatar
        if request_user.role.role == 'doctor':
            avatar_url = obj.patient.avatar.url if obj.patient.avatar else None
        elif request_user.role.role == 'patient':
            avatar_url = obj.doctor.avatar.url if obj.doctor.avatar else None
        else:
            avatar_url = None

        # Build absolute URL if avatar exists
        if avatar_url and request:
            return request.build_absolute_uri(avatar_url)
        return None
