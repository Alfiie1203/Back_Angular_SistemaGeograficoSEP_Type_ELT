from django.contrib import admin
from .models.formulario import Formulario
from .models.question import Question, QuestionHistory




class FormularioAdmin(admin.ModelAdmin):
    list_display = ['pk', 'proforestform', 'allocating_company', 'assigned_company', 'status_form']
    list_filter =   ['proforestform', 'revision_status']

admin.site.register(Formulario, FormularioAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'created_at', 'question_bank', 'formulario', 'last_modified', 'status']

admin.site.register(Question, QuestionAdmin)


class QuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'created_at', 'question', 'reviewed_by']

admin.site.register(QuestionHistory, QuestionHistoryAdmin)



