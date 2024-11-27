from rest_framework import serializers

from medicalBook.models import MedicalBook
from users.models import User


class MedicalBookSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()

    class Meta:
        model = MedicalBook
        fields = ('id', 'patient_name', 'patient_id', 'doctor_name', 'doctor_id', 'diagnosis', 'description',
                  'treatment', 'tests', 'created_at')

    def get_tests(self, obj):
        request = self.context.get('request')
        if obj.tests:
            return request.build_absolute_uri(obj.tests.url)
        return None

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}"

    def doctor_id(self, obj):
        return obj.doctor.id

    def patient_id(self, obj):
        return obj.patient.id


class CreateMedicalBookSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(roles__role='patient'))

    class Meta:
        model = MedicalBook
        fields = ('patient', 'doctor', 'diagnosis', 'description', 'treatment', 'tests')
        extra_kwargs = {
            'patient': {'required': True},
            'doctor': {'required': False},
            'tests': {'required': False}
        }

    def create(self, validated_data):
        patient = validated_data['patient']
        request = self.context.get('request')
        doctor = request.user if request else None

        if not doctor or doctor.roles.role != 'doctor':
            raise serializers.ValidationError("You are not a doctor")

        diagnosis = validated_data.get('diagnosis')
        treatment = validated_data.get('treatment')
        description = validated_data.get('description')
        tests = validated_data.get('tests', None)

        medicalbook = MedicalBook.objects.create(
            patient=patient,
            doctor=doctor,
            diagnosis=diagnosis,
            description=description,
            treatment=treatment,
            tests=tests
        )

        return medicalbook
