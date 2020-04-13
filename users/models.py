from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Clinician(models.Model):
    user_id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return "Clinician #" + str(self.user_id)


class Patient(models.Model):
    user_id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    clinician_id = models.ForeignKey(Clinician, null=True, on_delete=models.SET_NULL)
    younger_age_band = models.BooleanField()
    part_1_is_active = models.BooleanField(default=True)
    part_2_is_active = models.BooleanField(default=False)
    current_attempt_number = models.IntegerField(default=1)

    def __str__(self):
        return "Patient #" + str(self.user_id)

    def username(self):
        return self.user_id.username

    def password(self):
        return self.user_id.password


class Preferences(models.Model):
    user_id = models.OneToOneField(Patient, on_delete=models.CASCADE)
    theme = models.IntegerField(default=0)
    haptic = models.BooleanField(default=True)
    text_to_speech = models.BooleanField(default=True)

    def __str__(self):
        return self.user_id.user_id.username
