from django.contrib import admin

from .models import Patient, Clinician

admin.site.register([Patient, Clinician])
