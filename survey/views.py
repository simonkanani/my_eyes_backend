from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView, UpdateAPIView
from survey.models import Survey, Question, Response
from survey.serializers import SurveySerializer, QuestionSerializer, ResponseSerializer, PatientSurveySerializer
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.response import Response as RestResponse
from users.models import Patient

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
            return RestResponse("Question does not exist", status=404)
        else:
            serializer = self.serializer_class(question)
            return RestResponse(serializer.data, status=201)


class QuestionPostView(CreateAPIView):
    """Add a Question to a Survey"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ResponsePostView(CreateAPIView):
    """Submit a User Response to a Survey Question"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def post(self, request):
        patient = Patient.objects.get(user_id=request.data['patient_id'])
        request.data.update({'attempt_number': patient.current_attempt_number})
        serializer = ResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data, status=201)
        return RestResponse(serializer.errors, status=400)


class ResponseUpdateView(UpdateAPIView):
    """Update a previously provided answer"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def get_object(self):
        return self.queryset.get(id=self.kwargs['id'])

    def put(self, request, *args, **kwargs):
        try:
            self.kwargs['id'] = request.data['id']
            self.queryset.get(id=self.kwargs['id'])
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=400)
        except ValidationError as e:
            return RestResponse(e.__str__(), status=400)
        else:
            return self.update(request, *args, **kwargs)


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
            return RestResponse(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(response)
            return RestResponse(serializer.data, status=201)


class ResponseListView(ListAPIView):
    """Return a single User's Responses to all questions within a Survey"""
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        survey_name = self.kwargs['survey_name']
        attempt_number = self.kwargs['attempt_number']
        return self.queryset.filter(patient_id__user_id_id=patient_id, question_id__survey_id__name=survey_name, attempt_number=attempt_number)

    def list(self, *args, **kwargs):
        try:
            results = self.filter_queryset(self.get_queryset())
            if not results:
                raise ObjectDoesNotExist("No results found")
            else:
                serializer = self.get_serializer(results, many=True)
                return RestResponse(serializer.data, status=200)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=404)


class SurveyGetView(RetrieveAPIView):
    """Return details for a single Survey"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get(self, request, survey_name):
        try:
            survey = self.queryset.get(name=survey_name)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(survey)
            return RestResponse(serializer.data, status=201)


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
            return RestResponse(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                return RestResponse(serializer.data, status=200)
            else:
                return RestResponse(data, status=404)


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
                return RestResponse(serializer.data, status=200)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=404)














