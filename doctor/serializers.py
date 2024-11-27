from patient.models import Appointment
from rest_framework import serializers
from users.models import User, Role, SubRole
import secrets
import string


class DoctorSerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField()
    sub_role = serializers.StringRelatedField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'roles', 'sub_role')

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class DoctorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('access_key', 'roles')
        extra_kwargs = {
            'access_key': {'read_only': True}
        }

    def create(self, validated_data):

        access_key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))

        try:
            doctor_role = Role.objects.get(role='doctor')
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role": "Role 'doctor' does not exist."})

        # Создаем пользователя через менеджер, чтобы пароль хешировался
        user = User.objects.create_user(
            access_key=access_key,
            role=doctor_role,
        )
        return user


class DoctorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'sub_role', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'sub_role': {'required': False},  # Позволяем необязательное поле
        }

    def update(self, instance, validated_data):
        # Извлекаем пароль, если он есть
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)  # Хешируем пароль

        # Обрабатываем поле sub_role, если оно присутствует
        sub_role_name = validated_data.pop('sub_role', None)
        if sub_role_name:
            try:
                sub_role = SubRole.objects.get(sub_role=sub_role_name)
                instance.sub_role = sub_role
            except SubRole.DoesNotExist:
                raise serializers.ValidationError({"sub_role": "Invalid sub_role."})

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()  # Сохраняем изменения
        return instance
