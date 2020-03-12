from rest_framework import serializers
from .models import Patient, Clinician

class ClinicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinician
        fields = ['user_id']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['user_id', 'username', 'password', 'younger_age_band']