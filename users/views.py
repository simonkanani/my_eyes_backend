from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json, random, string
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, GenericAPIView, UpdateAPIView
from users.serializers import *
from django.db import transaction
from rest_framework.response import Response as RestResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse
from survey.models import Survey, Question, Response
import datetime


class PatientGenerateView(GenericAPIView):
    """
    Randomly generates 5-digit Username & 6-digit Password credentials for Patients, validating against existing Users to ensure there are no duplicated entries.
    """

    serializer_class = PatientGeneratorSerializer
    queryset = User.objects.all()

    def get(self, request):
        try:
            random_username = ''.join(random.choices(string.digits + string.ascii_uppercase, k=5))
            while self.queryset.filter(username=random_username).exists():
                random_username = ''.join(random.choices(string.digits + string.ascii_uppercase, k=5))
            random_password = ''.join(random.choices(string.digits, k=6))

            data = {'username': random_username, 'password': random_password}
            serializer = PatientGeneratorSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            return RestResponse(serializer.data, status=201)
        except Exception as e:
            return RestResponse(e.__str__(), status=400)


class PatientSaveView(CreateAPIView):
    """
    Registers a patient to the My Eyes Application.
    """
    serializer_class = PatientCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user_id = self.__generate_user(request)
                response = self.__generate_patient(request, user_id)
                self.__generate_preferences(response)
        except Exception as e:
            response = RestResponse(e.__str__(), status=400)
        finally:
            return response

    def __generate_user(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return user.id

    def __generate_patient(self, request, user_id):
        request.data.update({'user_id': user_id})
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.object = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return RestResponse(request.data, status=201,  headers=headers)

    def __generate_preferences(self, response):
        patient = Patient.objects.get(user_id=response.data.get('user_id'))
        default_preferences = Preferences.objects.create(user_id=patient)
        default_preferences.save()


class PatientRetrieveView(RetrieveAPIView):
    """
    Retrieve details about a single Patient
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'user_id'


class PatientSearchView(RetrieveAPIView):
    """
    Lists all patients currently registered on the Application.
    """

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get(self, request, *args, **kwargs):
        try:
           username = kwargs['username']
           patient = Patient.objects.get(user_id__username=username)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=404)
        else:
            serializer = self.serializer_class(patient)
            response = serializer.data
            response['attempts'], response['time_taken'] = self.count_attempts_and_time_taken(patient)
            return RestResponse(response, status=200)

    @staticmethod
    def count_attempts_and_time_taken(patient):
        attempts = {}
        time_taken = {}
        if patient.younger_age_band:
            surveys = [Survey.objects.get(name='FVQ_C'), Survey.objects.get(name='VQoL_C')]
        else:
            surveys = [Survey.objects.get(name='FVQ_YP'), Survey.objects.get(name='VQoL_YP')]
        for survey in surveys:
            time_taken[survey.name] = []
            count = 0
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


class PatientActivateView(UpdateAPIView):
    """
    Manually Activate or Deactivate a Patient's Part 1 or Part 2 Survey permissions
    """
    queryset = Patient.objects.all()
    serializer_class = PatientActivateSerializer
    lookup_field = 'user_id'

    def put(self, request, *args, **kwargs):
        try:
            user_id = kwargs['user_id']
            patient = Patient.objects.get(user_id=user_id)
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=400)
        except ValidationError as e:
            return RestResponse(e.__str__(), status=400)
        else:
            if request.data['increment_attempt']:
                current_attempt_number = patient.current_attempt_number + 1
            else:
                current_attempt_number = patient.current_attempt_number
            request.data.update({'current_attempt_number': current_attempt_number})
            return self.update(request, *args, **kwargs)


class PreferencesRetrieveView(RetrieveAPIView):
    """
    Retrieve details about a single Patient's Preferences
    """
    queryset = Preferences.objects.all()
    serializer_class = PreferenceSerializer
    lookup_field = 'user_id'


class PreferencesUpdateView(UpdateAPIView):
    """
    Update a single Patient's Preferences
    """
    queryset = Preferences.objects.all()
    serializer_class = PreferenceSerializer
    lookup_field = 'user_id'

    def put(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        try:
            Patient.objects.get(user_id=user_id)
            request_user_id = User.objects.get(id=request.data['user_id']).id
            if user_id != request_user_id:
                raise ValidationError("Inconsistent Request. Check User ID in URL against request JSON.")
        except ObjectDoesNotExist as e:
            return RestResponse(e.__str__(), status=400)
        except ValidationError as e:
            return RestResponse(e.__str__(), status=400)
        else:
            return self.update(request, *args, **kwargs)


@csrf_exempt
def login(request):
    """Authenticate via login"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                serializer = UserSerializer(user)
                if serializer.data['user_type'] == 'Clinician' or serializer.data['user_type'] == 'Patient':
                    return JsonResponse(serializer.data, status=200)
                else:
                    return JsonResponse('Invalid user_type', status=400, safe=False)
            else:
                return JsonResponse('Invalid Login Details', status=400, safe=False)
        else:
            return JsonResponse('Bad Request: ' + request.method, status=400, safe=False)
    except Exception as e:
        return JsonResponse(e.__str__(), status=404, safe=False)


