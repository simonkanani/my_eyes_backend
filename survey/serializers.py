from rest_framework import serializers
from .models import Survey, Question, Response
import collections


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question', 'question_number', 'survey_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['survey'] = instance.survey_id.name
        return data


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['patient_id', 'question_id', 'response']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['response_description'] = instance.get_response_key()
        data['time_stamp'] = instance.time_stamp
        data['survey'] = instance.question_id.survey_id.name
        data['question_number'] = instance.question_id.question_number
        data.pop('question_id')
        return data



class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['name']

    def to_representation(self, instance):
        data = collections.OrderedDict()
        data['id'] = instance.id
        data['name'] = instance.name
        data['Number of Questions'] = instance.number_of_questions()
        data['Patients Completed'] = instance.number_of_patients_completed()
        return data


