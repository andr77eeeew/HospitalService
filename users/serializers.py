from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from users.models import Role, SubRole
from django.utils.translation import gettext as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role',
                  "sub_role")


class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'gender', 'date_birth', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'style': {'input_type': 'password'}
        }

    def create(self, validated_data):
        # Попробуем получить роль пациента, обработаем исключение, если роль не найдена
        try:
            patient_role = Role.objects.get(role='patient')
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role": "Role 'patient' does not exist."})

        # Извлекаем и проверяем пароль
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # Создаем пользователя через менеджер, чтобы пароль хешировался
        user = User.objects.create_user(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
            role=patient_role,
            gender=validated_data.get('gender'),
            date_birth=validated_data.get('date_birth'),
            password=password,  # передаем пароль
        )
        return user


class PatientLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(_('User is deactivated.'))
            else:
                raise serializers.ValidationError(_('Invalid login credentials.'))
        else:
            raise serializers.ValidationError(_('Must include "username" and "password".'))

        data['user'] = user
        return data



