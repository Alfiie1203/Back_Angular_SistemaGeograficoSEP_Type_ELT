from django.urls import path
from .views import validate_coordinates_views, validate_traceability_views, verify_coordinates_views, verify_traceability_views


urlpatterns = [

# ========================  Coordinates Endpoints  ===============================
    path('general/colaborators/list/', validate_coordinates_views.ColaboratorsValidatorVerificatorApi.as_view()),       #los que validan nivel uno


    #========       Validar Compañias y Trazabilidades
    path('view/validation/company/list/', validate_coordinates_views.CompanyAdminValidationList.as_view()),
    path('validators/list/', validate_coordinates_views.ListValidatorsApi.as_view()),       #los que validan nivel uno
    path('asign/companyvalidator/<int:pk>/', validate_coordinates_views.CompanyAsignValidator.as_view()),

    #
    path('asign/list/company/validator/', validate_coordinates_views.CompanyAsignListValidator.as_view()),
    #

    path('view/validation/traceability/list/', validate_traceability_views.TraceabilityAdminValidationList.as_view()),
    path('asign/validation/traceability/list/', validate_traceability_views.AsignValidatorTraceabilityList.as_view()),

    path('validation/company/list/', validate_coordinates_views.CompanyValidationList.as_view()),
    path('validation/detail/<int:pk>/', validate_coordinates_views.CompanyValidateDetail.as_view()),
    path('validate/company/<int:pk>/', validate_coordinates_views.ValidateCompanyView.as_view()),
    
    path('traceability/validate/', validate_traceability_views.TraceabilityValidateCoordinatesList.as_view()), #las asignadas al validador
    path('traceability/validate/update/<int:pk>/', validate_traceability_views.TraceabilityUpdateValidation.as_view()), #las asignadas al validador
    path('traceability/validateresume/company/', validate_traceability_views.ResumeValitationByCompany.as_view()), #nueva resumen por compañia
    path('traceability/validateresume/company/sendmail/', validate_traceability_views.ResumeValidationCompanyEmail.as_view()), #Al invocarlo manda el resumen de validacion hasta el momento

    #=========      Verificar Compañias y Trazabilidades
    path('view/verification/company/list/', verify_coordinates_views.CompanyAdminVerificationList.as_view()),
    path('verificators/list/', verify_coordinates_views.ListVerificadorApi.as_view()),    #los que Verifican nivel 2 
    path('asign/companyverificator/<int:pk>/', verify_coordinates_views.CompanyAsignVerificator.as_view()),
    
    #
    path('asign/list/company/verificator/', verify_coordinates_views.CompanyAsignListVerificator.as_view()),
    #

    path('view/verification/traceability/list/', verify_traceability_views.TraceabilityAdminVerificationList.as_view()), #la que ve el SUPERADMINISTRADOR
    path('asign/verification/traceability/list/', verify_traceability_views.AsignVerificationTraceabilityList.as_view()),

    path('verification/company/list/', verify_coordinates_views.CompanyVerifyList.as_view()),
    path('verification/detail/<int:pk>/', verify_coordinates_views.CompanyVerifyDetail.as_view()),
    path('verification/company/<int:pk>/', verify_coordinates_views.VerifyCompanyView.as_view()),

    path('traceability/verify/', verify_traceability_views.TraceabilityVerifyCoordinatesList.as_view()), #la QUE VE EL VERIFICADOR
    path('traceability/verify/update/<int:pk>/', verify_traceability_views.TraceabilityUpdateVerification.as_view()), #las asignadas al verificador
    path('traceability/verifyresume/company/', verify_traceability_views.ResumeVerificationByCompany.as_view()), #nueva resumen por compañia
    path('traceability/verifyresume/company/sendmail/', verify_traceability_views.ResumeVerificationCompanyEmail.as_view()), #Al invocarlo manda el resumen de verificaciion hasta el momento


    

]