from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from .models import Clinician, Patient
import json

import random
import string

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the users index.")


def generate_patient(request):
    random_username = ''.join(random.choices(string.digits + string.ascii_uppercase, k=5))
    while User.objects.filter(username=random_username).exists():
        random_username = ''.join(random.choices(string.digits + string.ascii_uppercase, k=5))

    random_password = ''.join(random.choices(string.digits, k=6))

    return HttpResponse("Your random ID is: " + random_username + "<br/>Your random Password is: " + random_password)


@csrf_exempt
def add_patient(request):
    try:
        if request.method == 'POST':
            username = request.POST.__getitem__('username')
            password = request.POST.__getitem__('password')
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # clinician_id = request.POST.__getitem__('requestor')
            # clinician = Clinician.objects.filter(user_id=clinician_id)
            # patient = Patient(user_id=user, clinician=clinician)
            # patient.save()

            return HttpResponse("Patient Successfully Registered!")
        else:
            return HttpResponse("Bad Request!")
    except Exception:
        return HttpResponse("Error occurred! Please try again!")

@csrf_exempt
def login(request):
    # try:
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        print(username + " " + password)
        if user is not None:
            if Clinician.objects.filter(user_id=user).exists():
                return HttpResponse("Clinician")
            elif Patient.objects.filter(user_id=user).exists():
                return HttpResponse("Patient")
            else:
                return HttpResponse("Database Error - User does not have a User Type!")
        else:
            return HttpResponse("Invalid Login")
    else:
        return HttpResponse("Bad Request!")
    # except Exception:
    #     return HttpResponse("Error occurred! Please try again!")
