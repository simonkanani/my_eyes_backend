from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate', views.generate_patient, name="generate_id"),
    path('register', views.register_patient, name="register"),
]