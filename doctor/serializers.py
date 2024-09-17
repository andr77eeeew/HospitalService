from patient.models import Appointment
from rest_framework import serializers
from users.models import User, Role, SubRole
from django.utils.translation import gettext as _



class DoctorSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    sub_role = serializers.StringRelatedField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role', 'sub_role')

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class AppointmentTimesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('time')