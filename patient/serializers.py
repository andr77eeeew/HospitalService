from rest_framework import serializers
from users.models import User, Role


class PatientSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role')

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


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