from django.urls import path
from . import views
from rest_framework import routers

urlpatterns = [
    path('<str:survey_name>/<int:question_number>/', views.QuestionGetView.as_view()),
    path('post_question/', views.QuestionPostView.as_view()),
    path('<int:patient_id>/<str:survey_name>/<int:question_number>/', views.ResponseGetView.as_view()),
    path('post_response/', views.ResponsePostView.as_view()),
    path('<int:patient_id>/<str:survey_name>/', views.ResponseListView.as_view()),
    path('<str:survey_name>/', views.SurveyGetView.as_view())
]

