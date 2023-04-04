from django.urls import path
from rest_framework import routers
from .views import export_import_views 
from .views import traceability_views 



urlpatterns = [
# ========================  Traceability Endpoints  ===============================
    path('xlsx/create/', export_import_views.TraceabilityCreate.as_view()),
    path('xlsx/create/others/', export_import_views.TraceabilityOtherActorCreate.as_view()),
    #Template Url
    path('xlsx/export/', export_import_views.XlsxExportView.as_view(), name=export_import_views.XlsxExportView.url_name),
    path('xlsx/export-others/', export_import_views.XlsxExportOthersView.as_view(), name=export_import_views.XlsxExportOthersView.url_name),
    #API Url
    path('api/xlsx/export/', export_import_views.XlsxExportApi.as_view()),
    path('api/xlsx/exportothers/', export_import_views.XlsxExportOthersApi.as_view()),
    path('api/xlsx/traceability-export/', export_import_views.XlsxExportTraceabilityView.as_view()),


    path('create/', traceability_views.TraceabilityCreate.as_view()),
    path('view/<int:pk>/', traceability_views.TraceabilityView.as_view()),
    path('update/<int:pk>/', traceability_views.TraceabilityUpdate.as_view()),
    path('list/', traceability_views.TraceabilityList.as_view()),
    path('collaborator/list/', traceability_views.TraceabilityColaboratorList.as_view()),

    # path('company/search/', traceability_views.TraceabilitySearchCompany.as_view()),
    path('file/export/', traceability_views.TraceabilityFileExport.as_view()),

    path('mycompany/', traceability_views.GetMyCompany.as_view()),



]

