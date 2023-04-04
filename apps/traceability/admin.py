from django.contrib import admin
from .models.traceability import Traceability, TraceabilityFile, ValidateTraceability, VerifyTraceability
# Register your models here.

class TraceabilityAdmin(admin.ModelAdmin):
    list_display = ['pk', 'year', 'period', 'reported_company', 'supplier_company', 'purchased_volume','status_revision']
    list_filter = ('year', 'period', 'reported_company', 'status_revision')

admin.site.register(Traceability, TraceabilityAdmin)

class TraceabilityFileAdmin(admin.ModelAdmin):
    list_display = ['pk', 'upload_by', 'reporting_company' ]

admin.site.register(TraceabilityFile, TraceabilityFileAdmin)

class ValidateTraceabilityAdmin(admin.ModelAdmin):
    list_display = ['pk', 'traceability', 'date_validation']
admin.site.register(ValidateTraceability, ValidateTraceabilityAdmin)

class VerifyTraceabilityAdmin(admin.ModelAdmin):
    list_display = ['pk', 'traceability', 'date_verification']
admin.site.register(VerifyTraceability, VerifyTraceabilityAdmin)
