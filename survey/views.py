from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView, UpdateAPIView
from survey.models import Survey, Question, Response
from survey.serializers import SurveySerializer, QuestionSerializer, ResponseSerializer, PatientSurveySerializer
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.response import Response as RestResponse
from users.models import Patient
import datetime


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
        return self.queryset.filter(patient_id__user_id_id=patient_id, question_id__survey_id__name=survey_name,
                                    attempt_number=attempt_number)

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

    def get(self, request, patient_id, survey_name, attempt_number):
        try:
            survey = Survey.objects.get(name=survey_name)
            patient = Patient.objects.get(user_id=patient_id)
            data = {
                'survey_name': survey.name,
                'patient_id': patient.user_id.id,
                'number_of_questions': survey.number_of_questions(),
                'answered': survey.responses_submitted(patient, attempt_number)
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


class GetScores(RetrieveAPIView):
    """Returns scores for all completed attempts for a single Patient"""
    queryset = Response.objects.all()
    serializer_class = PatientSurveySerializer

    def get(self, request, *args, **kwargs):
        try:
            patient_id = kwargs['patient_id']
            patient = Patient.objects.get(user_id=patient_id)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=404)
        else:
            if patient.younger_age_band:
                survey_1_name = 'FVQ_C'
                survey_2_name = 'VQoL_C'
            else:
                survey_1_name = 'FVQ_YP'
                survey_2_name = 'VQoL_YP'
            survey_1 = Survey.objects.get(name=survey_1_name)
            survey_2 = Survey.objects.get(name=survey_2_name)
            current_attempt_number = patient.current_attempt_number
            scores = {survey_1_name: [], survey_2_name: []}
            for attempt_number in range(current_attempt_number):
                if survey_1.is_completed(patient, attempt_number+1):
                    responses = self.queryset.filter(patient_id__user_id_id=patient_id,
                                                     question_id__survey_id__name=survey_1_name,
                                                     attempt_number=attempt_number+1)
                    scores[survey_1_name].append(self.calculate_score(responses, survey_1_name))
                if survey_2.is_completed(patient, attempt_number+1):
                    responses = self.queryset.filter(patient_id__user_id_id=patient_id,
                                                     question_id__survey_id__name=survey_2_name,
                                                     attempt_number=attempt_number+1)
                    scores[survey_2_name].append(self.calculate_score(responses, survey_2_name))
            if len(scores[survey_1_name]) > 0:
                return RestResponse(scores, status=200)
            else:
                return RestResponse("0 Results Found", status=404)

    @staticmethod
    def calculate_score(responses, survey_name):
        summary_score = 0
        score = 0
        if 'FVQ' in survey_name:
            for response in responses:
                summary_score += response.response - 1
            if '_YP' in survey_name:
                scoring_table = {
                    0: 0.00,
                    1: 8.41,
                    2: 13.45,
                    3: 16.53,
                    4: 18.80,
                    5: 20.63,
                    6: 22.18,
                    7: 23.52,
                    8: 24.73,
                    9: 25.82,
                    10: 26.82,
                    11: 27.75,
                    12: 28.62,
                    13: 29.44,
                    14: 30.21,
                    15: 30.95,
                    16: 31.65,
                    17: 32.33,
                    18: 32.97,
                    19: 33.60,
                    20: 34.20,
                    21: 34.79,
                    22: 35.36,
                    23: 35.91,
                    24: 36.45,
                    25: 36.98,
                    26: 37.49,
                    27: 38.00,
                    28: 38.49,
                    29: 38.98,
                    30: 39.45,
                    31: 39.92,
                    32: 40.38,
                    33: 40.84,
                    34: 41.29,
                    35: 41.73,
                    36: 42.17,
                    37: 42.60,
                    38: 43.03,
                    39: 43.46,
                    40: 43.88,
                    41: 44.30,
                    42: 44.71,
                    43: 45.13,
                    44: 45.54,
                    45: 45.94,
                    46: 46.35,
                    47: 46.75,
                    48: 47.15,
                    49: 47.55,
                    50: 47.95,
                    51: 48.74,
                    52: 49.13,
                    53: 49.53,
                    54: 49.92,
                    55: 56.54,
                    56: 50.31,
                    57: 50.70,
                    58: 51.09,
                    59: 51.49,
                    60: 51.88,
                    61: 52.27,
                    62: 52.67,
                    63: 53.06,
                    64: 53.45,
                    65: 53.85,
                    66: 54.25,
                    67: 54.95,
                    68: 55.05,
                    69: 55.45,
                    70: 55.85,
                    71: 56.26,
                    72: 56.67,
                    73: 57.08,
                    74: 57.49,
                    75: 57.91,
                    76: 58.33,
                    77: 58.75,
                    78: 59.18,
                    79: 59.61,
                    80: 60.05,
                    81: 60.49,
                    82: 60.94,
                    83: 61.39,
                    84: 61.85,
                    85: 62.32,
                    86: 62.79,
                    87: 63.27,
                    88: 63.76,
                    89: 64.26,
                    90: 64.77,
                    91: 65.29,
                    92: 65.82,
                    93: 66.37,
                    94: 66.93,
                    95: 67.51,
                    96: 68.11,
                    97: 68.73,
                    98: 69.37,
                    99: 70.03,
                    100: 70.73,
                    101: 71.46,
                    102: 72.24,
                    103: 73.06,
                    104: 73.93,
                    105: 74.88,
                    106: 75.91,
                    107: 77.04,
                    108: 78.32,
                    109: 79.79,
                    110: 81.54,
                    111: 83.73,
                    112: 86.71,
                    113: 91.66,
                    114: 100
                }
            else:
                scoring_table = {
                    0: 0.00,
                    1: 9.40,
                    2: 15.00,
                    3: 18.39,
                    4: 20.88,
                    5: 22.87,
                    6: 24.55,
                    7: 26.01,
                    8: 27.31,
                    9: 28.49,
                    10: 29.57,
                    11: 30.57,
                    12: 31.51,
                    13: 32.39,
                    14: 33.22,
                    15: 34.02,
                    16: 34.78,
                    17: 35.51,
                    18: 36.22,
                    19: 36.90,
                    20: 37.56,
                    21: 38.21,
                    22: 38.83,
                    23: 39.44,
                    24: 40.04,
                    25: 40.63,
                    26: 41.20,
                    27: 41.77,
                    28: 42.33,
                    29: 42.88,
                    30: 43.42,
                    31: 43.96,
                    32: 44.49,
                    33: 45.01,
                    34: 45.54,
                    35: 46.06,
                    36: 46.57,
                    37: 47.09,
                    38: 47.60,
                    39: 48.11,
                    40: 48.62,
                    41: 49.13,
                    42: 49.64,
                    43: 50.16,
                    44: 50.67,
                    45: 51.19,
                    46: 51.70,
                    47: 52.22,
                    48: 52.75,
                    49: 53.27,
                    50: 53.80,
                    51: 54.34,
                    52: 54.88,
                    53: 55.43,
                    54: 55.98,
                    55: 56.54,
                    56: 57.11,
                    57: 57.69,
                    58: 58.28,
                    59: 58.87,
                    60: 59.48,
                    61: 60.10,
                    62: 60.74,
                    63: 61.39,
                    64: 62.06,
                    65: 62.74,
                    66: 63.45,
                    67: 64.18,
                    68: 64.94,
                    69: 65.73,
                    70: 66.55,
                    71: 67.41,
                    72: 68.31,
                    73: 69.27,
                    74: 70.29,
                    75: 71.39,
                    76: 72.59,
                    77: 73.91,
                    78: 75.39,
                    79: 77.08,
                    80: 79.08,
                    81: 81.59,
                    82: 84.99,
                    83: 90.59,
                    84: 100
                }
            score = scoring_table[summary_score]
        else:

            if '_YP' in survey_name:
                for response in responses:
                    num = response.question_id.question_number
                    if num == 8 or num == 9 or num == 15 or num == 17 or num == 20:
                        if response.response-1 == 2:
                            summary_score += 1
                        if response.response-1 == 1:
                            summary_score += 2
                        if response.response-1 == 0:
                            summary_score += 3
                    else:
                        summary_score += response.response - 1
                scoring_table = {
                    0: 0.00,
                    1: 10.82,
                    2: 17.08,
                    3: 20.77,
                    4: 23.41,
                    5: 25.48,
                    6: 27.20,
                    7: 28.68,
                    8: 29.98,
                    9: 31.14,
                    10: 32.21,
                    11: 33.19,
                    12: 34.10,
                    13: 34.96,
                    14: 35.78,
                    15: 36.55,
                    16: 37.29,
                    17: 38.01,
                    18: 38.70,
                    19: 39.37,
                    20: 40.03,
                    21: 40.67,
                    22: 41.30,
                    23: 41.91,
                    24: 42.52,
                    25: 43.12,
                    26: 43.72,
                    27: 44.31,
                    28: 44.90,
                    29: 45.49,
                    30: 46.07,
                    31: 46.66,
                    32: 47.25,
                    33: 47.84,
                    34: 48.44,
                    35: 49.04,
                    36: 46.57,
                    37: 49.65,
                    38: 50.26,
                    39: 51.51,
                    40: 52.15,
                    41: 52.81,
                    42: 53.48,
                    43: 54.16,
                    44: 54.86,
                    45: 55.58,
                    46: 56.31,
                    47: 57.08,
                    48: 57.86,
                    49: 58.68,
                    50: 59.52,
                    51: 60.40,
                    52: 61.33,
                    53: 62.30,
                    54: 63.32,
                    55: 64.41,
                    56: 65.57,
                    57: 66.82,
                    58: 68.18,
                    59: 69.69,
                    60: 71.38,
                    61: 73.32,
                    62: 75.63,
                    63: 78.52,
                    64: 82.49,
                    65: 88.98,
                    66: 100.00,
                }
                score = scoring_table[summary_score]
            else:
                for response in responses:
                    num = response.question_id.question_number
                    if num == 3 or num == 7 or num == 8 or num == 15 or num == 16 or num == 18 or num == 20:
                        if response.response-1 == 2:
                            summary_score += 1
                        if response.response-1 == 1:
                            summary_score += 2
                        if response.response-1 == 0:
                            summary_score += 3
                    else:
                        summary_score += response.response - 1
                scoring_table = {
                    0: 0.00,
                    1: 11.26,
                    2: 17.88,
                    3: 21.84,
                    4: 24.71,
                    5: 26.99,
                    6: 28.90,
                    7: 30.55,
                    8: 32.01,
                    9: 33.33,
                    10: 34.54,
                    11: 35.66,
                    12: 36.70,
                    13: 37.68,
                    14: 38.61,
                    15: 39.50,
                    16: 40.35,
                    17: 41.17,
                    18: 41.96,
                    19: 42.72,
                    20: 43.46,
                    21: 44.19,
                    22: 44.90,
                    23: 45.59,
                    24: 46.28,
                    25: 46.95,
                    26: 47.62,
                    27: 48.28,
                    28: 48.94,
                    29: 49.59,
                    30: 50.24,
                    31: 50.89,
                    32: 51.54,
                    33: 52.19,
                    34: 52.84,
                    35: 53.50,
                    36: 54.17,
                    37: 54.84,
                    38: 55.53,
                    39: 56.22,
                    40: 56.93,
                    41: 57.66,
                    42: 58.41,
                    43: 59.17,
                    44: 59.97,
                    45: 60.80,
                    46: 61.66,
                    47: 62.56,
                    48: 63.52,
                    49: 64.53,
                    50: 65.62,
                    51: 66.80,
                    52: 68.09,
                    53: 69.52,
                    54: 71.15,
                    55: 73.03,
                    56: 75.30,
                    57: 78.16,
                    58: 82.11,
                    59: 88.73,
                    60: 100.00,
                }
                score = scoring_table[summary_score]
        return score


class GetSummaryData(RetrieveAPIView):
    """Returns Summary Usage Data of Server"""
    def get(self, request):
        response = {'registered': self.registered(),
                    'attempts': self.count_attempts_and_time_taken()[0],
                    'average_completion_time': self.count_attempts_and_time_taken()[1]}
        return RestResponse(response, status=200)

    @staticmethod
    def count_attempts_and_time_taken():
        attempts = {}
        time_taken = {}
        for survey in Survey.objects.all():
            time_taken[survey.name] = []
            count = 0
            for patient in Patient.objects.all():
                for i in range(1, patient.current_attempt_number+1):
                    if survey.is_completed(patient, i):
                        time_taken[survey.name].append(survey.time_taken(patient, i))
                        count += 1
            if time_taken[survey.name]:
                time_taken[survey.name] = sum(time_taken[survey.name], datetime.timedelta(0)) / len(time_taken[survey.name])
            else:
                time_taken[survey.name] = 0
            attempts[survey.name] = count
        return attempts, time_taken

    @staticmethod
    def registered():
        registered = {}
        now = datetime.datetime.now()
        first_of_month = datetime.datetime(now.year, now.month, 1)
        registered['Child'] = Patient.objects.filter(younger_age_band=True).count()
        registered['Child_new'] = Patient.objects.filter(younger_age_band=True, user_id__date_joined__range=(first_of_month, now)).count()
        registered['Young_Person'] = Patient.objects.filter(younger_age_band=False).count()
        registered['Young_Person_new'] = Patient.objects.filter(younger_age_band=False, user_id__date_joined__range=(first_of_month, now)).count()
        return registered
