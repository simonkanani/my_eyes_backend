from django.db import models
from users.models import Patient
from django.db.models import Min, Max

# Create your models here.


class Survey(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def number_of_questions(self):
        return Question.objects.filter(survey_id=self).count()

    def responses_submitted(self, patient, attempt_number):
        responses = Response.objects.filter(question_id__survey_id=self, patient_id=patient, attempt_number=attempt_number)
        return responses.count()

    def is_completed(self, patient, attempt_number):
        if self.number_of_questions() == self.responses_submitted(patient, attempt_number):
            return True
        else:
            return False

    def number_of_attempts(self):
        attempts = 0
        patients = Patient.objects.all()
        for patient in patients:
            attempts += Response.objects.filter(question_id__survey_id=self, patient_id=patient).\
                        values('attempt_number').distinct().count()
        return attempts

    def number_of_patients_completed(self):
        count = 0
        patients = Patient.objects.all()
        for patient in patients:
            if self.is_completed(patient):
                count += 1
        return count

    def time_taken(self, patient, attempt_number):
        started = list(Response.objects.filter(question_id__survey_id=self, patient_id=patient, attempt_number=attempt_number).aggregate(Min('time_stamp')).values())[0]
        ended = list(Response.objects.filter(question_id__survey_id=self, patient_id=patient, attempt_number=attempt_number).aggregate(Max('time_stamp')).values())[0]
        return ended-started


class Question(models.Model):
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE, default=None)
    question_number = models.IntegerField()
    question = models.CharField(max_length=150)

    def __str__(self):
        return self.question

    class Meta:
        unique_together = ('question_number', 'survey_id')


class Response(models.Model):
    RESPONSE_OPTIONS = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    ]

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, default=None)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.IntegerField(choices=RESPONSE_OPTIONS)
    attempt_number = models.IntegerField()
    time_stamp = models.DateTimeField(auto_now=True)

    def get_response_key(self):
        return ResponseKey.objects.get(survey_id=self.question_id.survey_id, response=self.response).get_response_key_display()

    def survey_name(self):
        return self.question.survey.name

    class Meta:
        unique_together = ('question_id', 'patient_id', 'attempt_number')


class ResponseKey(models.Model):
    RESPONSE_OPTIONS = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    ]

    RESPONSE_KEY_OPTIONS = [
        ('NT', 'NOT AT ALL TRUE'),
        ('LT', 'A LITTLE BIT TRUE'),
        ('MT', 'MOSTLY TRUE'),
        ('CT', 'COMPLETELY TRUE'),
        ('VD', 'VERY DIFFICULT'),
        ('D', 'DIFFICULT'),
        ('E', 'EASY'),
        ('VE', 'VERY EASY'),
    ]
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE)
    response = models.IntegerField(choices=RESPONSE_OPTIONS)
    response_key = models.CharField(max_length=2, choices=RESPONSE_KEY_OPTIONS)

    class Meta:
        unique_together = ('survey_id', 'response')
