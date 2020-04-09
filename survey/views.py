from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView
from survey.models import Survey, Question, Response
from survey.serializers import SurveySerializer, QuestionSerializer, ResponseSerializer, PatientSurveySerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response as r
from rest_framework import viewsets
from users.models import Patient
from rest_framework.decorators import action

# Create your views here.


class QuestionGetView(RetrieveAPIView):
    """Returns a specific Question within a Survey"""

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get(self, request, survey_name, question_number):
        try:
            survey = Survey.objects.get(name=survey_name)
            question = self.queryset.get(survey_id=survey, question_number=question_number)
        except ObjectDoesNotExist:
            return r("Question does not exist",  status=404)
        else:
            serializer = self.serializer_class(question)
            return r(serializer.data, status=201)


class QuestionPostView(CreateAPIView):
    """Add a Question to a Survey"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ResponsePostView(CreateAPIView):
    """Submit a User Response to a Survey Question"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def post(self, request):
        serializer = ResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return r(serializer.data, status=201)
        return r(serializer.errors, status=400)


class ResponseGetView(RetrieveAPIView):
    """Return a User Response to a single Survey Question"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def get(self, request, survey_name, question_number, patient_id):
        try:
            survey_id = Survey.objects.get(name=survey_name)
            question_id = Question.objects.get(survey_id=survey_id, question_number=question_number)
            response = self.queryset.get(question_id=question_id, patient_id=patient_id)
        except ObjectDoesNotExist as e:
            return r(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(response)
            return r(serializer.data, status=201)


class ResponseListView(ListAPIView):
    """Return a single User's Responses to all questions within a Survey"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        survey_name = self.kwargs['survey_name']
        return self.queryset.filter(patient_id__user_id_id=patient_id, question_id__survey_id__name=survey_name)

    def list(self, *args, **kwargs):
        try:
            results = self.filter_queryset(self.get_queryset())
            if not results:
                raise ObjectDoesNotExist("No results found")
            else:
                serializer = self.get_serializer(results, many=True)
                return r(serializer.data, status=200)
        except ObjectDoesNotExist as e:
            return r(e.__str__(), status=404)


class SurveyGetView(RetrieveAPIView):
    """Return details for a single Survey"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get(self, request, survey_name):
        try:
            survey = self.queryset.get(name=survey_name)
        except ObjectDoesNotExist as e:
            return r(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(survey)
            return r(serializer.data, status=201)


class PatientSurveyGetView(RetrieveAPIView):
    """Returns details for a single Survey for a single Patient"""
    queryset = Survey.objects.all()
    serializer_class = PatientSurveySerializer

    def get(self, request, patient_id, survey_name):
        try:
            survey = Survey.objects.get(name=survey_name)
            patient = Patient.objects.get(user_id=patient_id)
            data = {
                'survey_name': survey.name,
                'patient_id': patient.user_id.id,
                'number_of_questions': survey.number_of_questions(),
                'answered': survey.responses_submitted(patient)
            }
        except ObjectDoesNotExist as e:
            return r(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                return r(serializer.data, status=200)
            else:
                return r(data, status=404)


class QuestionListView(ListAPIView):
    """Lists all Questions within a Survey"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        survey_name = self.kwargs['survey_name']
        return self.queryset.filter(survey_id__name=survey_name)

    def list(self, *args, **kwargs):
        try:
            results = self.filter_queryset(self.get_queryset())
            if not results:
                raise ObjectDoesNotExist("No results found")
            else:
                serializer = self.get_serializer(results, many=True)
                return r(serializer.data, status=200)
        except ObjectDoesNotExist as e:
            return r(e.__str__(), status=404)














