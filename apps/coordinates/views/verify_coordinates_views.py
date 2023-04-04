from apps.emailcustom.models import EmailTemplate
from apps.user.serializers.user_serializers import CollaboratorSerializer
from apps.user.models import User
from apps.supplybase.models.supplybase import SupplyBase
from apps.utils.permissions import CustomDjangoModelPermission

from apps.company.models.company import Company, ValidateCompany, VerifyCompany
from django.contrib.auth.models import Group

from datetime import datetime as dt

from ..serializers.company_serializer import  CompanySerializerView, CompanySerializerEdit

from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

import time 

@permission_classes([CustomDjangoModelPermission])
class CompanyAdminVerificationList(generics.ListAPIView):
    serializer_class = CompanySerializerView

    def get_queryset(self):
        verificadorgroup = Group.objects.get(name='VALIDADOR')
        queryset = Company.objects.filter(status=True).exclude(validator_user__groups = verificadorgroup)

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
        verificadorgroup = Group.objects.get(name='VALIDADOR')
        queryset = Company.objects.filter(status=True).exclude(validator_user__groups = verificadorgroup)

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
        response.data['sin_verificar'] = queryset.filter(status_revision='NVE').count()
        response.data['verificadas'] = queryset.filter(status_revision='VE').count()

        try:
            response.data['porcentaje_verificadas'] = round(((queryset.filter(status_revision='VE').count()*100))/queryset.count(),1)
        except:
            response.data['porcentaje_verificadas'] = 0
        try:
            response.data['porcentaje_no_verificadas'] = round((queryset.filter(status_revision='NVE').count()*100)/queryset.count(),1)
        except:
            response.data['porcentaje_no_verificadas'] = 0
        try:
            response.data['porcentaje_sin_revisar'] = round(((queryset.filter(status_revision='SR').count())*100)/queryset.count(),1)
        except:
            response.data['porcentaje_sin_revisar'] = 0
        return response

@permission_classes([IsAuthenticated])
class CompanyAsignListVerificator(APIView):
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
            try:
                user_validator = User.objects.get(id=usuario_id)
                emails = [user_validator.email]
                EmailTemplate.send(
                    'assigned_as_company_verificator',
                    {
                        'assigned_verificator': user_validator.get_full_name(),
                        'in_verification_company': ', '.join(list(queryset.values_list('name', flat = True))),
                        'end_date_validation': end_date_validation
                    },
                    emails = emails
                    )
                time.sleep(2)
            except:
                print("error sending email > CompanyAsignListValidator")


        return Response({'results': 'traceability asigned to validator', 'asignado': queryset.count()})


#=============================================================================
#================       VERIFY company traceability       ==================


@permission_classes([IsAuthenticated])
class ListVerificadorApi(generics.ListAPIView):

    serializer_class = CollaboratorSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role__name='COLABORADOR', groups__name='VERIFICADOR', status= True)
        return queryset


@permission_classes([IsAuthenticated])
class CompanyAsignVerificator(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerEdit

    def perform_update(self, serializer):
        start_date_validation = dt.strptime(self.request.data['start_date_validation'], "%Y-%m-%d").date()
        end_date_validation = dt.strptime(self.request.data['end_date_validation'], "%Y-%m-%d").date()
        
        today = dt.now().date()
        if (start_date_validation >= today) and (end_date_validation > today) :
            serializer.save(
                # status_revision = 'NVE',
            )
            obj = self.get_object()
            verificadores = self.request.data['validator_user']
            for verificador_id in verificadores:
                user_verificador = User.objects.get(id=verificador_id)
                emails = [user_verificador.email]
                EmailTemplate.send(
                    'assigned_as_company_verificator',
                    {
                        'assigned_verificator': user_verificador.get_full_name(),
                        'in_verification_company': obj.name,
                        'end_date_validation': obj.end_date_validation.strftime('%d/%m/%Y')
                    },
                    emails = emails
                )
                time.sleep(1)
        else:
            raise serializers.ValidationError("Assigned dates must not be less than today")

#

@permission_classes([CustomDjangoModelPermission])
class CompanyVerifyList(generics.ListAPIView):
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
        response.data['sin_verificar'] = queryset.filter(status_revision='NVE').count()
        response.data['verificadas'] = queryset.filter(status_revision='VE').count()

        try:
            response.data['porcentaje_verificadas'] = round(((queryset.filter(status_revision='VE').count()*100))/queryset.count(),1)
        except:
            response.data['porcentaje_verificadas'] = 0
        try:
            response.data['porcentaje_no_verificadas'] = round((queryset.filter(status_revision='NVE').count()*100)/queryset.count(),1)
        except:
            response.data['porcentaje_no_verificadas'] = 0
        try:
            response.data['porcentaje_sin_revisar'] = round(((queryset.filter(status_revision='SR').count())*100)/queryset.count(),1)
        except:
            response.data['porcentaje_sin_revisar'] = 0
        return response

@permission_classes([IsAuthenticated])
class CompanyVerifyDetail(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerView


@permission_classes([IsAuthenticated])
class VerifyCompanyView(generics.UpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializerEdit

    def perform_update(self, serializer):
        data = self.request.data
        serializer.save( status_revision = data['validated'])
        verification_note = data['note_validation']
        company = self.get_object()
        if company.actor_type.is_productor == True:
            try:
                company_creadora = SupplyBase.objects.filter(supplier_company = company)[0].company
                company_emails = User.objects.filter(company = company_creadora).values_list('email', flat=True)
            except:
                company_emails = User.objects.filter(id=1).none()
        else:
            company_emails = User.objects.filter(company = company).values_list('email', flat=True)

        if data['validated'] =='VE':
            validate = True
        else:
            validate = False
        if company_emails.count() > 0:
            EmailTemplate.send(
                'verify_coordinates_of_company',
                {
                    'company_name' : company.name,
                    'verification_note': verification_note,
                    'company_latitude': company.latitude,
                    'company_longitude': company.longitude,
                    'company_country': company.country.name,
                    'company_region': company.region.name,
                    'company_city': company.city.name,
                    'validate': validate,
                },
                emails = company_emails
            )

        VerifyCompany.objects.create(
            company = company,
            message = verification_note,
            autor = self.request.user
        )


