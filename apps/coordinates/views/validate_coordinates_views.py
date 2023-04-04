from apps.utils.permissions import CustomDjangoModelPermission
from apps.emailcustom.models import EmailTemplate
from apps.supplybase.models.supplybase import SupplyBase

from rest_framework.decorators import permission_classes

from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


from django.db.models import Q
from django.contrib.auth.models import Group

from datetime import datetime as dt


from apps.company.models.company import Company, ValidateCompany, VerifyCompany
from ..serializers.company_serializer import  CompanySerializerView, CompanySerializerEdit
from rest_framework.permissions import IsAuthenticated

from apps.user.serializers.user_serializers import CollaboratorSerializer
from apps.user.models import User

import time

@permission_classes([CustomDjangoModelPermission])
class CompanyAdminValidationList(generics.ListAPIView): #Lista para el superadmin para que asigne
    serializer_class = CompanySerializerView

    def get_queryset(self):
        
        queryset = Company.objects.filter(status=True).exclude(status_revision='VE').exclude(status_revision='NVE')

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')
        name = self.request.GET.get('name')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if name:
            queryset = queryset.filter(name__icontains =name)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = Company.objects.filter(status=True).exclude(status_revision='VE').exclude(status_revision='NVE')

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')
        name = self.request.GET.get('name')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if name:
            queryset = queryset.filter(name__icontains =name)

        response = super().list(request, *args, **kwargs)
        response.data['total'] = queryset.count()
        response.data['sin_revisar'] = queryset.filter(status_revision='SR').count()
        response.data['sin_validar'] = queryset.filter(status_revision='NV').count()
        response.data['validadas'] = queryset.filter(status_revision='VA').count()

        try:
            response.data['porcentaje_validadas'] = round(((queryset.filter(status_revision='VA').count()*100))/queryset.count(),1)
        except:
            response.data['porcentaje_validadas'] = 0
        try:
            response.data['porcentaje_no_validadas'] = round((queryset.filter(status_revision='NV').count()*100)/queryset.count(),1)
        except:
            response.data['porcentaje_no_validadas'] = 0
        try:
            response.data['porcentaje_sin_revisar'] = round(((queryset.filter(status_revision='SR').count())*100)/queryset.count(),1)
        except:
            response.data['porcentaje_sin_revisar'] = 0
        
        return response
    
@permission_classes([IsAuthenticated])
class CompanyAsignListValidator(APIView):
    serializer_class = CompanySerializerView

    def post(self, request):
        queryset = Company.objects.filter(status=True)
        commodity = request.data['commodity']
        actor_type = request.data['actor_type']
        name = request.data['name']
        usuarios_asignados = request.data['validator_user']

        start_date_validation = dt.strptime(request.data['start_date_validation'], "%Y-%m-%d").date()
        
        end_date_validation = dt.strptime(request.data['end_date_validation'], "%Y-%m-%d").date()

        today = dt.now().date()
        if (start_date_validation >= today) and (end_date_validation > today) :
            pass

        else:

            return Response(
                {
                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "assigned_dates",
                            "detail": "Assigned dates must not be less than today",
                            "attr": "Assigned Dates"
                        }
                    ]
                },
                403
            )
        
        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if name:
            queryset = queryset.filter(name__icontains =name)

        queryset.update(start_date_validation= start_date_validation, end_date_validation = end_date_validation)

        for company in queryset:
            company.validator_user.set(usuarios_asignados, clear=True)
            company.save()

        for usuario_id in usuarios_asignados:
            # try:
            user_validator = User.objects.get(id=usuario_id)
            emails = [user_validator.email]
            EmailTemplate.send(
                'assigned_as_company_validator',
                {
                    'assigned_validator': user_validator.get_full_name(),
                    'in_validation_company': ', '.join(list(queryset.values_list('name', flat = True))),
                    'end_date_validation': end_date_validation
                },
                emails = emails
                )
            time.sleep(2)


        return Response({'results': 'traceability asigned to validator', 'asignado': queryset.count()})

#endpoint para traer validadores y verificadores para listarlos en las tablas
@permission_classes([IsAuthenticated])
class ColaboratorsValidatorVerificatorApi(generics.ListAPIView):
    serializer_class = CollaboratorSerializer

    def get_queryset(self):
        queryset = User.objects.filter(Q(role__name='COLABORADOR', groups__name='VALIDADOR', status= True) | Q(role__name='COLABORADOR', groups__name='VERIFICADOR', status= True))
        return queryset

#=============================================================================
#================       Validate company traceability       ==================

# Enpoint para enviar colaborators al crear un nuevo formulario


@permission_classes([IsAuthenticated])
class ListValidatorsApi(generics.ListAPIView):
    serializer_class = CollaboratorSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role__name='COLABORADOR', groups__name='VALIDADOR', status= True)
        return queryset


@permission_classes([IsAuthenticated])
class CompanyAsignValidator(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerEdit

    def perform_update(self, serializer):
        start_date_validation = dt.strptime(self.request.data['start_date_validation'], "%Y-%m-%d").date()
        end_date_validation = dt.strptime(self.request.data['end_date_validation'], "%Y-%m-%d").date()
        today = dt.now().date()
        if (start_date_validation >= today) and (end_date_validation > today) :
            serializer.save(
                # status_revision = 'NV',
            )
            obj = self.get_object()
            validadores = self.request.data['validator_user']
            for validador in validadores:
                user_validator = User.objects.get(id=validador)
                emails = [user_validator.email]
                EmailTemplate.send(
                    'assigned_as_company_validator',
                    {
                        'assigned_validator': user_validator.get_full_name(),
                        'in_validation_company': obj.name,
                        'end_date_validation': obj.end_date_validation.strftime('%d/%m/%Y')
                    },
                    emails = emails
                )
                time.sleep(1)

        else:
            raise serializers.ValidationError("Assigned dates must not be less than today")
        
    


@permission_classes([CustomDjangoModelPermission])
class CompanyValidationList(generics.ListAPIView): #Vista del validador
    serializer_class = CompanySerializerView

    def get_queryset(self):
        queryset = Company.objects.filter(validator_user = self.request.user)

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')
        name = self.request.GET.get('name')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if name:
            queryset = queryset.filter(name__icontains =name)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = Company.objects.filter(validator_user = self.request.user)

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')
        name = self.request.GET.get('name')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if name:
            queryset = queryset.filter(name__icontains =name)

        response = super().list(request, *args, **kwargs)
        response.data['total'] = queryset.count()
        response.data['sin_revisar'] = queryset.filter(status_revision='SR').count()
        response.data['sin_validar'] = queryset.filter(status_revision='NV').count()
        response.data['validadas'] = queryset.filter(status_revision='VA').count()

        try:
            response.data['porcentaje_validadas'] = round(((queryset.filter(status_revision='VA').count()*100))/queryset.count(),1)
        except:
            response.data['porcentaje_validadas'] = 0
        try:
            response.data['porcentaje_no_validadas'] = round((queryset.filter(status_revision='NV').count()*100)/queryset.count(),1)
        except:
            response.data['porcentaje_no_validadas'] = 0
        try:
            response.data['porcentaje_sin_revisar'] = round(((queryset.filter(status_revision='SR').count())*100)/queryset.count(),1)
        except:
            response.data['porcentaje_sin_revisar'] = 0
        
        return response

@permission_classes([IsAuthenticated])
class CompanyValidateDetail(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerView


@permission_classes([IsAuthenticated])
class ValidateCompanyView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerEdit

    def perform_update(self, serializer):
        data = self.request.data
        serializer.save( status_revision = data['status_revision'])
        validation_note = data['note_revision']
        company = self.get_object()
        if company.actor_type.is_productor == True:
            try:
                company_creadora = SupplyBase.objects.filter(supplier_company = company)[0].company
                company_emails = User.objects.filter(company = company_creadora).values_list('email', flat=True)
            except:
                company_emails =User.objects.filter(id=1).none()
        else:
            company_emails = User.objects.filter(company = company).values_list('email', flat=True)

        if data['status_revision'] =='VA':
            validate = True
        else:
            validate = False

        if company_emails.count() > 0:
            EmailTemplate.send(
                'validate_coordinates_of_company',
                {
                    'company_name' : company.name,
                    'validator_note': validation_note,
                    'company_latitude': company.latitude,
                    'company_longitude': company.longitude,
                    'company_country': company.country.name,
                    'company_region': company.region.name,
                    'company_city': company.city.name,
                    'validate': validate,
                },
                emails = company_emails
            )

        ValidateCompany.objects.create(
            company = company,
            message = validation_note,
            autor = self.request.user,
            status_revision = data['status_revision']
        )





@permission_classes([IsAuthenticated])
class CompanyValidateList(generics.ListAPIView):
    serializer_class = CompanySerializerView

    def get_queryset(self):
        most_recent_expiration = self.request.GET.get('most_recent_expiration')

        if most_recent_expiration=='true':
            queryset = Company.objects.filter(validator_user = self.request.user).order_by('end_date_validation')
        else:
            queryset = Company.objects.filter(validator_user = self.request.user)

        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)

        return queryset


#==============================================================

