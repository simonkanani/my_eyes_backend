from django.contrib import admin

from .models import Patient, Clinician, Preferences


class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'younger_age_band', 'clinician', 'part_1_is_active',
                    'part_2_is_active', 'current_attempt_number')

    def clinician(self, obj):
        return obj.clinician_id

    def username(self, obj):
        return obj.user_id

    def password(self, obj):
        return obj.user_id.password

    def id(self, obj):
        return obj.user_id.id


admin.site.register([Clinician, Preferences])
admin.site.register(Patient, PatientAdmin)