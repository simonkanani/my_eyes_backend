from django.contrib import admin

from .models import Survey, Question, Response, ResponseKey


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey_id', 'question_number', 'question')


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey_id', 'question_id', 'patient_id', 'answer', 'answer_description', 'attempt_number', 'time_stamp')

    def survey_id(self, obj):
        return obj.question_id.survey_id

    def answer(self, obj):
        return str(obj.response)

    def answer_description(self, obj):
        return obj.get_response_key()


class ResponseKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey_id', 'answer_id', 'answer_key', 'answer_description')

    def answer_id(self, obj):
        return str(obj.response)

    def answer_key(self, obj):
        return obj.response_key

    def answer_description(self, obj):
        return obj.get_response_key_display()


admin.site.register([Survey])
admin.site.register(Question, QuestionAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(ResponseKey, ResponseKeyAdmin)
