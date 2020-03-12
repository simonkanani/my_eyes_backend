from django.urls import path
from . import views
from rest_framework.authtoken import views as v

urlpatterns = [
    path('', views.index),
    path('generate_patient', views.generate_patient),
    path('add_patient', views.add_patient),
    path('login', views.login),
]