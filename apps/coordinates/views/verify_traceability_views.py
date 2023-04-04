from apps.company.models.company import Company
from apps.user.views.groups import Check_user_in_groups
from apps.traceability.models.traceability import Traceability, VerifyTraceability
from apps.utils.permissions import CustomDjangoModelPermission
from apps.emailcustom.models import EmailTemplate
from apps.user.models import User

from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework import generics
from django.db.models import Q
from datetime import datetime as dt

from ..serializers.traceability_serializer import (TraceabilityUpdateSerializer, TraceabilityVerifySerializer)
from ..serializers.company_serializer import CompanyResumeVerificationSerializer

import time

@permission_classes([CustomDjangoModelPermission])
class TraceabilityAdminVerificationList(generics.ListAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityVerifySerializer

    def get_queryset(self):
        queryset = Traceability.objects.all() #.exclude(status_revision='VE')
        commodity = self.request.GET.get('commodity')
        actor_type = self.request.GET.get('actor_type')
        period = self.request.GET.get('period')
        year = self.request.GET.get('year')
        name = self.request.GET.get('name')
        status_revision = self.request.GET.get('status_revision')
        validator_id = self.request.GET.get('validator_id')

        if commodity:
            queryset = queryset.filter(commodity__id = commodity)
        if actor_type:
            queryset = queryset.filter(actor_type__id = actor_type)
        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )
        if year:
            queryset = queryset.filter(year = year)
        if name:
            queryset = queryset.filter(reported_company__name__icontains = name)
        if status_revision:
            queryset = queryset.filter(status_revision = status_revision)

        if validator_id == '':
            pass
        elif validator_id == 0 or validator_id == None :
            queryset = queryset.filter(validator_user = None)
        else:
            queryset = queryset.filter(validator_user__in = [validator_id])
        

        return queryset

@permission_classes([IsAuthenticated])
class AsignVerificationTraceabilityList(APIView):

    def post(self, request):
        queryset = Traceability.objects.all()
        commodity = request.data['commodity']
        actor_type = request.data['actor_type']
        period = request.data['period']
        year = request.data['year']
        name = request.data['name']
        status_revision = request.data['status_revision']
        validator_id = request.data['validator_id']

        usuarios_asignados = request.data['revisor_id']
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
        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )
        if year:
            queryset = queryset.filter(year = year)
        if name:
            queryset = queryset.filter(reported_company__name__icontains = name)
        if status_revision:
            queryset = queryset.filter(status_revision = status_revision)
        
        if validator_id == '':
            pass
        elif validator_id == 0 or validator_id == None :
            queryset = queryset.filter(validator_user = None)
        else:
            queryset = queryset.filter(validator_user__in = [validator_id])

        total_mod = queryset.count()
        queryset.update(start_date_validation= start_date_validation, end_date_validation = end_date_validation)

        for trazabilidad in queryset:
            trazabilidad.validator_user.set(usuarios_asignados, clear=True)
            trazabilidad.save
        
        for usuario_id in usuarios_asignados:
            try:
                usuario_asignado = User.objects.get(id = usuario_id)
                emails = [usuario_asignado.email]

                EmailTemplate.send(
                    'assigned_as_traceability_verificator',
                    {
                        'assigned_validator': usuario_asignado.get_full_name(),
                        'registers_no_traceability': total_mod,
                        'deadline_validation': end_date_validation
                    },
                    emails = emails,
                )
                time.sleep(2)
            except:
                print("Error sending email > AsignVerificationTraceabilityList ")

        return Response({'results': 'traceability asigned to validator', 'asignado': total_mod})


@permission_classes([CustomDjangoModelPermission])
class TraceabilityVerifyCoordinatesList(generics.ListAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityVerifySerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

    def get_queryset(self):
        groups = ['VERIFICADOR', 'VALIDADOR']
        if Check_user_in_groups(self.request.user, groups):
            queryset = Traceability.objects.filter(validator_user__in = [self.request.user])
        else:
            queryset = Traceability.objects.all()
        
        period = self.request.GET.get('period')
        year = self.request.GET.get('year')
        reported_company_id = self.request.GET.get('reported_company_id')
        status_revision = self.request.GET.get('status_revision')
        #periodo de validacion
        start_date_validation = self.request.GET.get('start_date_validation')
        end_date_validation = self.request.GET.get('end_date_validation')

        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )
        if year:
            queryset = queryset.filter(year = year)
        if reported_company_id:
            queryset = queryset.filter(reported_company__id = reported_company_id)
        if status_revision:
            queryset = queryset.filter(status_revision = status_revision)

        if start_date_validation:
            start_date = dt.strptime(start_date_validation, "%Y-%m-%d").date()
            queryset = queryset.filter(start_date_validation__gte = start_date)
        if end_date_validation:
            end_date = dt.strptime(end_date_validation, "%Y-%m-%d").date()
            queryset = queryset.filter(end_date_validation__lte = end_date)

        return queryset

    def list(self, request, *args, **kwargs):
        groups = ['VERIFICADOR', 'VALIDADOR']
        if Check_user_in_groups(self.request.user, groups):
             queryset = Traceability.objects.filter(validator_user = self.request.user)
        else:
            queryset = Traceability.objects.all()

        period = self.request.GET.get('period')
        year = self.request.GET.get('year')
        reported_company_id = self.request.GET.get('reported_company_id')
        #periodo de validacion
        start_date_validation = self.request.GET.get('start_date_validation')
        end_date_validation = self.request.GET.get('end_date_validation')

        if (year and year != ''):
            queryset = queryset.filter( year = year )
        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )
        if reported_company_id:
            queryset = queryset.filter(reported_company__id = reported_company_id)
        
        if start_date_validation:
            start_date = dt.strptime(start_date_validation, "%Y-%m-%d").date()
            queryset = queryset.filter(start_date_validation__gte = start_date)
        if end_date_validation:
            end_date = dt.strptime(end_date_validation, "%Y-%m-%d").date()
            queryset = queryset.filter(end_date_validation__lte = end_date)

        response = super().list(request, *args, **kwargs)
        response.data['total'] = queryset.count()
        response.data['no_verificadas'] = queryset.filter(status_revision='NVE').count()
        response.data['verificadas'] = queryset.filter(status_revision='VE').count()
        response.data['sin_revisar'] = queryset.filter(status_revision='SR').count()+queryset.filter(status_revision='NV').count()+queryset.filter(status_revision='VA').count()

        try:
            response.data['porcentaje_verificadas'] = round((queryset.filter(status_revision='VE').count()*100)/queryset.count(), 1)
        except:
            response.data['porcentaje_verificadas'] = 0
        try:
            response.data['porcentaje_no_verificadas'] = round((queryset.filter(status_revision='NVE').count()*100)/queryset.count(), 1)
        except:
            response.data['porcentaje_no_verificadas'] = 0
        try:
            response.data['porcentaje_sin_revisar'] = round(((queryset.filter(status_revision='SR').count()+queryset.filter(status_revision='NV').count()+queryset.filter(status_revision='VA').count())*100)/queryset.count(), 1)
        except:
            response.data['porcentaje_sin_revisar'] = 0
        #prepare dict of companies to pass to fornt
        if Check_user_in_groups(self.request.user, groups):
            queryset_company = Traceability.objects.filter(validator_user = self.request.user)
        else:
            queryset_company = Traceability.objects.all()
        traceabilitys = queryset_company.values('reported_company')
        companies = Company.objects.filter(id__in = traceabilitys).distinct()
        array = []
        for company in companies:
            dict = {}
            dict['name_company'] = company.name
            dict['id_company'] = company.id
            
            array.append(dict)
        response.data['list_companies'] = array

        return response

@permission_classes([IsAuthenticated])
class TraceabilityUpdateVerification(generics.UpdateAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityUpdateSerializer

    def perform_update(self, serializer):
        data = self.request.data
        serializer.save( status_revision = data['verified'] )
        verification_note = data['verification_note']
        VerifyTraceability.objects.create(
            traceability = self.get_object(),
            message = verification_note,
            autor = self.request.user,
            status_revision = data['verified']
        )
        
@permission_classes([IsAuthenticated])
class ResumeVerificationCompanyEmail(APIView):
    def get(self, request ):
        company  = Company.objects.get(id = self.request.query_params.get('reported_company_id'))
        company_emails = User.objects.filter(company = company).values_list('email', flat=True)

        queryset = Traceability.objects.filter(reported_company=company, validator_user = self.request.user)
        total = queryset.count()
        
        verificadas = queryset.filter(status_revision='VE').count()
        query_year = Traceability.objects.filter(reported_company=company, validator_user = self.request.user).values('year').distinct().order_by('year')
        year = [year['year'] for year in query_year]
        query_period_text = Traceability.objects.filter(reported_company=company, validator_user = self.request.user).values('period').distinct().order_by('period')
        period = [period['period'] for period in query_period_text]
        period_text = []

        if 0 in period:
            period_text.append('Anual')
        if 1 in period:
            period_text.append('Semestre 1')
        if 2 in period:
            period_text.append('Semestre 2')
        try:
            porcentaje_avance = round((verificadas*100)/total)
        except:
            porcentaje_avance = 0
        
        if company_emails.count()>0:
            EmailTemplate.send(
                'verify_coordinates_of_traceability',
                {
                    'company_name' : company.name,
                    'year': year,
                    'period_text': period_text,
                    'total_traceability': total,
                    'porcentaje_avance': porcentaje_avance,
                },
                emails = company_emails
            )
            return Response({"mesagge": "Email sended to company sucessfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "not_found",
                            "detail": "The company has no user to notify",
                            "attr": "Email"
                        }
                    ]
                },
                404
            )


@permission_classes([IsAuthenticated])
class ResumeVerificationByCompany(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyResumeVerificationSerializer
    
    def get_queryset(self):
        groups = ['VERIFICADOR']
        period = self.request.GET.get('period')
        year = self.request.GET.get('year')
        company_name = self.request.GET.get('company_name')

        if Check_user_in_groups(self.request.user, groups):
            traceabilitys = Traceability.objects.filter(validator_user = self.request.user).values('reported_company')
            if period and period != '0':
                traceabilitys = traceabilitys.filter(period = period)
            if year and year != '':
                traceabilitys = traceabilitys.filter(year = year)

            queryset = Company.objects.filter(id__in = traceabilitys).distinct()
            if company_name and company_name !='':
                queryset = queryset.filter(name__icontains=company_name)

        else:
            traceabilitys = Traceability.objects.all().values('reported_company')
            if period and period != '0':
                traceabilitys = traceabilitys.filter(period = period)
            if year and year != '':
                traceabilitys = traceabilitys.filter(year = year)

            queryset = Company.objects.filter(id__in = traceabilitys).distinct()
            if company_name and company_name !='':
                queryset = queryset.filter(name__icontains=company_name)

        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        groups = ['VERIFICADOR']
        if Check_user_in_groups(self.request.user, groups):
            context["user_pk"] = self.request.user.id
        else:
            context["user_pk"] = None
        
        context["period"] = self.request.GET.get('period')
        context["year"] = self.request.GET.get('year')
        context["company_name"] = self.request.GET.get('company_name')

        return context