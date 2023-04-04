from django.contrib import admin
from .models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_key', 'subject', 'from_email', 'to_email']
    save_as = True
admin.site.register(EmailTemplate, EmailTemplateAdmin)