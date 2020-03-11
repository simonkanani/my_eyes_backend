from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Clinician(models.Model):
    user_id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return "Clinician #" + str(self.user_id)


class Patient(models.Model):
    user_id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    clinician = models.ForeignKey(Clinician, null=True, on_delete=models.SET_NULL)
    younger_age_band = models.BooleanField()

    def __str__(self):
        return "Patient #" + str(self.user_id)


class Preferences(models.Model):
    user_id = models.OneToOneField(Patient, on_delete=models.CASCADE)
    theme = models.IntegerField(default=0)

    def __str__(self):
        return self.theme
