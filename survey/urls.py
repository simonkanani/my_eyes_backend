from django.urls import path
from . import views
from rest_framework import routers

urlpatterns = [
    path('<str:survey_name>/summarize', views.SurveyGetView.as_view()),
    path('<str:survey_name>/all', views.QuestionListView.as_view()),
    path('<str:survey_name>/<int:question_number>', views.QuestionGetView.as_view()),
    path('<int:patient_id>/<str:survey_name>/<int:attempt_number>/summarize', views.PatientSurveyGetView.as_view()),
    path('<int:patient_id>/<str:survey_name>/<int:question_number>', views.ResponseGetView.as_view()),
    path('<int:patient_id>/<str:survey_name>/<int:attempt_number>/all', views.ResponseListView.as_view()),
    path('<int:patient_id>/scores', views.GetScores.as_view()),
    path('usage_data', views.GetSummaryData.as_view()),
    path('post_question', views.QuestionPostView.as_view()),
    path('post_response', views.ResponsePostView.as_view()),
    path('update_response', views.ResponseUpdateView.as_view())
]

