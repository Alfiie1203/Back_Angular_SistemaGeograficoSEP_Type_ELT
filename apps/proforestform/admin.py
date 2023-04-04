from django.contrib import admin
from .models.proforestform import ProforestForm, Period


class ProforestFormAdmin(admin.ModelAdmin):
    list_display = ['pk', 'code_form', 'name', 'created_at', 'status']

admin.site.register(ProforestForm, ProforestFormAdmin)

class PeriodAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'code']

admin.site.register(Period, PeriodAdmin)

