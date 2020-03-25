from rest_framework import serializers
from .models import Patient, User, Preferences


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = ['user_id', 'younger_age_band', 'clinician_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.username()
        data['password'] = instance.password()
        return data


class PatientCreateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = Patient
        fields = ['username', 'password', 'younger_age_band', 'clinician_id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_Patient', 'is_Clinician']


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = ['user_id', 'theme', 'haptic', 'text_to_speech']


class PatientGeneratorSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=5)
    password = serializers.CharField(max_length=6)
