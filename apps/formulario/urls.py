from django.urls import path
from .views import formulario_views, usercreate_views, validate_formularios, verificate_formularios, miscelanea_views

urlpatterns = [

    path('list/', formulario_views.FormularioList.as_view()), #se va a cambiar
    path('asign/', formulario_views.FormularioAsign.as_view()),

    path('asign/formemailcompany', formulario_views.FormularioEmailAsignCompany.as_view()),
    
    path('view/<int:pk>/', formulario_views.FormularioView.as_view()),

    path('list/asignedformularios/<int:pk>', formulario_views.AsignedFormulariosProforestform.as_view()),

    path('list_questions/<int:pk>/', formulario_views.FormularioDetail.as_view()),
    path('submitformulario/<int:pk>/', formulario_views.SubmitFormulario.as_view()),
    path('finishformulario/<int:pk>/', formulario_views.FinishFormulario.as_view()),        #Ruta que Finaliza el formulario
    path('retroalimentacionreview/<int:pk>/', formulario_views.FormularioFeedback.as_view()),        #Ruta que busca el formulario y el feedback


    path('response_answer/<int:pk>/', formulario_views.AnswerQuestion.as_view()),
    path('listcompanies/', formulario_views.ListCompanies.as_view()),
    path('checkversion/', formulario_views.CheckVersionFile.as_view()),
    
    path('usercreate/', usercreate_views.CreateUserKey.as_view()),
    
    path('listcompanies/noresponsable/', formulario_views.ListNoResponsableCompanies.as_view()),

    path('history_answer/<int:pk>/', formulario_views.HistoryQuestion.as_view()),

    path('list/assignedformsbyme/', formulario_views.ListFormulariosAssignedByMe.as_view()),
    
    # Ojo vista para ver todos los formularios asignados 
    path('list/assigned/detail/', formulario_views.ListAssignedForms.as_view()),
    #Validacion de formularios

    path('validate/list/formularios/', validate_formularios.ValidateListFormularios.as_view()),
    path('validate/assign/list/formularios/', validate_formularios.AssignValidateListFormularios.as_view()),
    path('validate/submitpartial/formulario/<int:pk>/', formulario_views.SubmitPartialValidateFormulario.as_view()),
    path('validate/submit/formulario/<int:pk>/', formulario_views.SubmitValidateFormulario.as_view()),
    #
    path('validate/assign/formulario/<int:pk>', validate_formularios.FormularioAssignValidators.as_view()),
    #

    
    #Verificacion de formularios

    path('verificate/list/formularios/', verificate_formularios.VerificateListFormularios.as_view()),
    path('verificate/assign/list/formularios/', verificate_formularios.AssignVerificateListFormularios.as_view()),
    path('verificate/submitpartial/formulario/<int:pk>/', formulario_views.SubmitPartialVerificateFormulario.as_view()),
    path('verificate/submit/formulario/<int:pk>/', formulario_views.SubmitVerificateFormulario.as_view()),
    #
    path('verificate/assign/formulario/<int:pk>', verificate_formularios.FormularioAssignVerificators.as_view()),
    #

    # Miscelaneas URLS
    path('list/proforestforms/idnames/', miscelanea_views.ProforestFormList.as_view()),
    path('list/proforestforms/period/', miscelanea_views.ProforestPeriodList.as_view()),



]

