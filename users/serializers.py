from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from django.utils.translation import gettext as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    sub_role = serializers.StringRelatedField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role',
                  "sub_role")

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class LoginSerializer(serializers.Serializer):
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


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'email', 'phone', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        # Извлекаем пароль, если он есть
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Обновляем остальные поля напрямую
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)

        # Сохраняем изменения
        instance.save()

        return instance
