from django.urls import path
from . import views
from rest_framework.authtoken import views as v


urlpatterns = [
    path('login', views.login),
    path('generate_patient', views.GeneratePatientView.as_view()),
    path('register_patient', views.RegisterPatientView.as_view()),
    path('list_patients', views.ListPatientView.as_view()),
    path('<int:user_id>', views.PatientView.as_view()),
    path('<int:user_id>/preferences/', views.PreferencesView.as_view()),
    path('update_preferences/', views.UpdatePreferencesView.as_view())
]
