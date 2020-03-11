from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate

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


def register_patient(request):
    try:
        if request.method == 'POST':
            username = request.POST.__getitem__('username')
            password = request.POST.__getitem__('password')

            user = User.objects.create_user(username=username, password=password)
            user.save()
            return HttpResponse("User Successfully Registered!")
        else:
            return HttpResponse("Bad Request!")
    except Exception:
        return HttpResponse("Error occurred! Please try again!" + Exception.__str__())


def login(request):
    try:
        if request.method == 'GET':
            username = ''
            password = ''

            user = authenticate

        else:
            return HttpResponse("Bad Request!")
    except Exception:
        return HttpResponse("Error occurred! Please try again!" + Exception.__str__())
