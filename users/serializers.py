from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import Role, SubRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'gender', 'date_birth', 'role', 'sub_role')


class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'gender', 'date_birth', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Get the patient role
        patient_role = Role.objects.get(role='patient')

        # Create the user with the patient role
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            role=patient_role,
            gender=validated_data['gender'],
            date_birth=validated_data['date_birth'],
        )
        return user


