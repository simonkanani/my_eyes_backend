from django.contrib import admin

from .models import Patient, Clinician, Preferences
from survey.models import Survey, Question, Response
from django.http import HttpResponse
import csv
import datetime
from survey.views import GetScores
from django.db.models import Max


class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'younger_age_band', 'clinician', 'part_1_is_active',
                    'part_2_is_active', 'current_attempt_number')

    actions = ['export_patient_data', 'export_survey_data']

    def clinician(self, obj):
        return obj.clinician_id

    def username(self, obj):
        return obj.user_id

    def password(self, obj):
        return obj.user_id.password

    def id(self, obj):
        return obj.user_id.id

    def export_patient_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patient_data.csv"'

        writer = csv.writer(response)
        header = ['User ID', 'Username', 'Age_Band', 'Date_Registered', 'Clinician', 'FVQ_Currently_Active',
                  'VQoL_Currently_Active', 'FVQ_Completed_Attempts', 'FVQ_Average_Score', 'FVQ_Max_Score',
                  'FVQ_Min_Score',
                  'FVQ_Average_Completion_Time', 'VQoL_Completed_Attempts', 'VQoL_Average_Score', 'VQoL_Max_Score',
                  'VQoL_Min_Score', 'VQoL_Average_Completion_Time', 'Theme', 'Haptic', 'Text_to_Speech']
        writer.writerow(header)

        patients = queryset
        for patient in patients:
            writer.writerow(self.gen_patient_data(patient))

        return response

    def gen_patient_data(self, patient):
        if patient.younger_age_band:
            age_band = "Child"
            fvq = 'FVQ_C'
            vqol = 'VQoL_C'
        else:
            age_band = "Young_Person"
            fvq = 'FVQ_YP'
            vqol = 'VQoL_YP'
        attempts, time_taken = self.count_attempts_and_time_taken(patient)
        scores = self.get_average_min_max_score(patient)
        preferences = Preferences.objects.get(user_id=patient)
        return [patient.user_id.id, patient.user_id.username, age_band, patient.user_id.date_joined,
                patient.clinician_id.user_id.username, patient.part_1_is_active, patient.part_2_is_active,
                attempts[fvq],
                scores[fvq], scores[fvq + '_max'], scores[fvq + '_min'], str(time_taken[fvq]), attempts[vqol],
                scores[vqol],
                scores[vqol + '_min'], scores[vqol + '_min'], time_taken[fvq], preferences.theme, preferences.haptic,
                preferences.text_to_speech]

    def count_attempts_and_time_taken(self, patient):
        if patient.younger_age_band:
            surveys = [Survey.objects.get(name='FVQ_C'), Survey.objects.get(name='VQoL_C')]
        else:
            surveys = [Survey.objects.get(name='FVQ_YP'), Survey.objects.get(name='VQoL_YP')]
        attempts = {}
        time_taken = {}
        for survey in surveys:
            time_taken[survey.name] = []
            count = 0
            for i in range(1, patient.current_attempt_number + 1):
                if survey.is_completed(patient, i):
                    time_taken[survey.name].append(survey.time_taken(patient, i))
                    count += 1
            if time_taken[survey.name]:
                time_taken[survey.name] = sum(time_taken[survey.name], datetime.timedelta(0)) / len(
                    time_taken[survey.name])
            else:
                time_taken[survey.name] = 0
            attempts[survey.name] = count
        return attempts, time_taken

    def get_average_min_max_score(self, patient):
        if patient.younger_age_band:
            age_band = "Child"
            fvq = 'FVQ_C'
            vqol = 'VQoL_C'
        else:
            age_band = "Young_Person"
            fvq = 'FVQ_YP'
            vqol = 'VQoL_YP'
        all_responses = Response.objects.filter(patient_id=patient)
        FVQ_scores = []
        VQoL_scores = []
        for attempt in range(1, patient.current_attempt_number + 1):
            responses = all_responses.filter(attempt_number=attempt)
            FVQ_scores.append(GetScores.calculate_score(responses, fvq))
            VQoL_scores.append(GetScores.calculate_score(responses, vqol))

            print(patient.user_id.username, "FVQ_Scores:")
            print(FVQ_scores)
            print(patient.user_id.username, "VQoL_Scores:")
            print(VQoL_scores)

        return {fvq: sum(FVQ_scores) / len(FVQ_scores),
                fvq + '_max': max(FVQ_scores),
                fvq + '_min': min(FVQ_scores),
                vqol: sum(VQoL_scores) / len(VQoL_scores),
                vqol + '_max': max(VQoL_scores),
                vqol + '_min': min(VQoL_scores)
                }

    def export_survey_data(self, request, queryset):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey_data.csv"'

        # The data is hard-coded here, but you could load it from a database or
        # some other source.
        max_q_num = Response.objects.all().aggregate(Max('question_id__question_number'))[
            'question_id__question_number__max']
        writer = csv.writer(response)
        header = ['User ID', 'Username', 'Age_Band', 'Date_Registered', 'Clinician', 'Survey_Name', 'Attempt', 'Score',
                  'Date_Completed', 'Time_Taken']
        for i in range(1, max_q_num + 1):
            header.append('Question ' + str(i))
        writer.writerow(header)

        patients = queryset
        for patient in patients:
            if patient.younger_age_band:
                age_band = "Child"
                fvq = 'FVQ_C'
                vqol = 'VQoL_C'
            else:
                age_band = "Young_Person"
                fvq = 'FVQ_YP'
                vqol = 'VQoL_YP'
            for attempt in range(1, patient.current_attempt_number + 1):
                survey = Survey.objects.get(name=fvq)
                if survey.is_completed(patient, attempt):
                    writer.writerow(self.gen_survey_data(patient, attempt, survey, age_band))
                survey = Survey.objects.get(name=vqol)
                if survey.is_completed(patient, attempt):
                    writer.writerow(self.gen_survey_data(patient, attempt, survey, age_band))

        return response

    def gen_survey_data(self, patient, attempt, survey, age_band):
        responses = Response.objects.filter(patient_id=patient, question_id__survey_id=survey, attempt_number=attempt)
        date_completed = responses.aggregate(Max('time_stamp'))['time_stamp__max']
        time_taken = survey.time_taken(patient, attempt)
        score = GetScores.calculate_score(responses, survey.name)
        row = [patient.user_id.id, patient.user_id.username, age_band, patient.user_id.date_joined,
               patient.clinician_id.user_id.username, survey.name, attempt, score, date_completed, "'"+str(time_taken)]
        for i in range(1, len(responses) + 1):
            row.append(responses.get(question_id__question_number=i).response)
        return row

    export_survey_data.short_description = "Export Survey Data"

    export_patient_data.short_description = "Export Patient Data"


admin.site.register([Clinician, Preferences])
admin.site.register(Patient, PatientAdmin)