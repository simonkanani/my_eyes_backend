from django.db import models
from users.models import Patient

# Create your models here.


class Survey(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def is_completed(self, patient):
        questions = Question.objects.filter(survey=self)
        responses = Response.objects.filter(question__survey=self, patient=patient)

        if questions.count() == responses.count():
            return True
        else:
            return False

    def number_of_questions(self):
        return Question.objects.filter(survey=self).count()

    def number_of_patients_completed(self):
        count = 0
        patients = Patient.objects.all()
        for patient in patients:
            if self.is_completed(patient):
                count +=1
        return count


class Question(models.Model):
    question_number = models.IntegerField()
    question = models.CharField(max_length=150)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.question

    class Meta:
        unique_together = ('question_number', 'survey')


class Response(models.Model):
    RESPONSE_OPTIONS = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.IntegerField(choices=RESPONSE_OPTIONS)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, default=None)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def get_response_key(self):
        return ResponseKey.objects.get(survey=self.question.survey, response=self.response).get_response_key_display()

    def survey_name(self):
        return self.question.survey.name

    class Meta:
        unique_together = ('question', 'patient')


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
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    response = models.IntegerField(choices=RESPONSE_OPTIONS)
    response_key = models.CharField(max_length=2, choices=RESPONSE_KEY_OPTIONS)

    class Meta:
        unique_together = ('survey', 'response')
