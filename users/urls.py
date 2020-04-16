from django.urls import path
from . import views
from rest_framework.authtoken import views as v


urlpatterns = [
    path('login', views.login),
    path('generate_patient', views.PatientGenerateView.as_view()),
    path('register_patient', views.PatientSaveView.as_view()),
    path('search_patients/<str:user_id__username>', views.PatientSearchView.as_view()),
    path('<int:user_id>', views.PatientRetrieveView.as_view()),
    path('<int:user_id>/preferences', views.PreferencesRetrieveView.as_view()),
    path('<int:user_id>/preferences/update', views.PreferencesUpdateView.as_view()),
    path('<int:user_id>/activate', views.PatientActivateView.as_view())
]
