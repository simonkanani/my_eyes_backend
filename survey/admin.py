from django.contrib import admin

from .models import Survey, Question, Response, ResponseKey


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'question_number', 'question')


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'question', 'patient_id', 'patient', 'answer', 'answer_description')

    def survey(self, obj):
        return obj.question.survey

    def answer(self, obj):
        return str(obj.response)

    def answer_description(self, obj):
        return obj.get_response_key()

    def patient_id(self, obj):
        return obj.patient.user_id.id


class ResponseKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'answer', 'answer_key')

    def answer(self, obj):
        return str(obj.response)

    def answer_key(self, obj):
        return obj.response_key


admin.site.register([Survey])
admin.site.register(Question, QuestionAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(ResponseKey, ResponseKeyAdmin)
