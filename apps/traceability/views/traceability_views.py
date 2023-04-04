from ..serializers.traceability_serializer import (TraceabilitySerializer, TraceabilityCreateSerializer, TraceabilityUpdateSerializer, TraceabilityColaboratorSerializer )
from ..models.traceability import Traceability

from cities_light.models import Country, Region, SubRegion


from apps.company.serializers.company_serializer import CompanySerializer
from apps.company.models.company import Company
from apps.company.models.commodity import Commodity
from apps.company.models.actor_type import ActorType
from apps.supplybase.models.supplybase import SupplyBase
from apps.utils.permissions import CustomDjangoModelPermission
from apps.user.views.groups import Check_user_in_groups

from django.db.models import Q
from django.http import HttpResponse

import datetime as dt
from import_export import fields, resources

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics

# ============================= RESOURCE EXPORT ===============================
class TraceabilitySpanishExportResource(resources.ModelResource):
    
    def dehydrate_reported_user(self, obj):
        if obj.reported_user:
            return obj.reported_user.get_full_name()
        else:
            return "No reported user"


    class Meta:
        model = Traceability
        fields =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_es',
            'actor_type__name_es',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )
        export_order =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_es',
            'actor_type__name_es',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )

class TraceabilityPortugueseExportResource(resources.ModelResource):
    
    def dehydrate_reported_user(self, obj):
        if obj.reported_user:
            return obj.reported_user.get_full_name()
        else:
            return "No reported user"

    
    class Meta:
        model = Traceability
        fields =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_pt',
            'actor_type__name_pt',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )
        export_order =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_pt',
            'actor_type__name_pt',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )

class TraceabilityEnglishExportResource(resources.ModelResource):
    def dehydrate_reported_user(self, obj):
        if obj.reported_user:
            return obj.reported_user.get_full_name()
        else:
            return "No reported user"

    class Meta:
        model = Traceability
        fields =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_en',
            'actor_type__name_en',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )
        export_order =(
            'id', 'date_reported',
            'reported_user', 'reported_company__name', 'supplier_company__name',
            'commodity__name_en',
            'actor_type__name_en',
            'company_group__name',
            'supplier_tax_number', 'supplier_capacity', 'supplier_production', 'purchased_volume', 'certification', 'latitude', 'longitude',
            'country__name', 'region__name', 'city__name',
            'year', 'period'
        )
from rest_framework import status


@permission_classes([CustomDjangoModelPermission])
class TraceabilityCreate(generics.CreateAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityCreateSerializer

    def create(self, request, *args, **kwargs):
        data = self.request.data
        year = data['year']
        period = data['period']
        try:
            id_empresa_reportada = data['id_empresa_reporta']
        except:
            id_empresa_reportada = self.request.user.company.id
        if Company.objects.filter(nit = data['nit'], commodity__id = data['commodity'],actor_type__id = data['actor_type']).exists():
            supplier_company= Company.objects.get(
                            nit = data['nit'],
                            commodity__id = data['commodity'],
                            actor_type__id = data['actor_type']
                            )
            if Traceability.objects.filter(year=year, period=period, reported_company__id=id_empresa_reportada, supplier_company=supplier_company).exists():
                
                return Response( {
                        "type": "validation_error",
                        "errors": [
                            {
                                "code": "existing_register",
                                "detail": "There is already a record for this company in this year and period",
                                "attr": "traceability"
                            }
                        ]
                    },
                    403)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        data = self.request.data
        user = self.request.user
        is_other_actor = data['otroActor']
        purchased_volume = round(float(data['purchased_volume'])/100, 5)
        try:
            id_empresa_reportada = data['id_empresa_reporta']
        except:
            id_empresa_reportada = self.request.user.company.id

        if Company.objects.filter(nit = data['nit'], commodity__id = data['commodity'],actor_type__id = data['actor_type']).exists():
            supplier_company= Company.objects.get(
                        nit = data['nit'],
                        commodity__id = data['commodity'],
                        actor_type__id = data['actor_type']
                        )
        else:
            supplier_company = Company.objects.create(
                        name = data['name'],
                        latitude = data['latitude'],
                        longitude =data['longitude'],
                        nit = data['nit'],
                        commodity = Commodity.objects.get(id=data['commodity']),
                        actor_type = ActorType.objects.get(id=data['actor_type']),
                        company_profile = 'SC' if is_other_actor=='false' else 'SO',
                        country = Country.objects.get(id = data['country']),
                        region = Region.objects.get(id = data['region']),
                        city = SubRegion.objects.get(id = data['city']),

            )

        serializer.save(
            reported_user = user,
            reported_company = user.company if user.company else Company.objects.get(id=id_empresa_reportada),
            supplier_company = supplier_company,
            supplier_name = data['name'],
            supplier_tax_number = data['nit'],
            purchased_volume = purchased_volume
        )

@permission_classes([CustomDjangoModelPermission])
class TraceabilityView(generics.RetrieveAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilitySerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

@permission_classes([CustomDjangoModelPermission])
class TraceabilityUpdate(generics.UpdateAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityUpdateSerializer

    def partial_update(self, request, *args, **kwargs): #esta funcion sirve para ajustar el porcentaje que viene del PATCH
        instance = self.get_object()
        incomming_volume = request.data.get('purchased_volume')
        volume = round(float(incomming_volume)/100, 5)
        if incomming_volume is not None:
            request.data['purchased_volume'] = volume

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


@permission_classes([CustomDjangoModelPermission])
class TraceabilityList(generics.ListAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilitySerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

    def get_queryset(self):
        groups = ['VERIFICADOR', 'VALIDADOR']
        if Check_user_in_groups(self.request.user, groups):
            queryset = Traceability.objects.filter(validator_user = self.request.user)
        else:
            groups_admin = ['SUPERADMINISTRADOR', 'ADMINISTRADOR']
            if Check_user_in_groups(self.request.user, groups_admin):
                queryset = Traceability.objects.all()
            elif self.request.user.company:
                queryset = Traceability.objects.filter(reported_company = self.request.user.company)
            else:
                queryset = Traceability.objects.none()

        year = self.request.query_params.get('year')
        period = self.request.query_params.get('period')
        search = self.request.query_params.get('search')
        reported_company_id = self.request.query_params.get('reported_company_id')
        supplier_company_id = self.request.query_params.get('supplier_company_id')

        

        pais = self.request.query_params.get('pais')
        region = self.request.query_params.get('region')
        ciudad = self.request.query_params.get('ciudad')

        commodity = self.request.query_params.get('commodity')
        tipo_actor = self.request.query_params.get('tipo_actor')


        

        if (year and year != ''):
            queryset = queryset.filter( year = year )
        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )


        if (pais  and pais !=''):
            queryset = queryset.filter(country__id=pais)

        if (region  and region !=''):
            queryset = queryset.filter(region__id=region)
        
        if (ciudad  and ciudad !=''):
            queryset = queryset.filter(city__id=ciudad)

        if (commodity and commodity!=''):
            queryset = queryset.filter(commodity__id = commodity)

        if (tipo_actor and commodity!=''):
            queryset = queryset.filter(actor_type__id = tipo_actor)

        if (reported_company_id and reported_company_id!=''):
            reported_company = Company.objects.get(id=reported_company_id)
            queryset = queryset.filter( reported_company = reported_company)
    
        if (supplier_company_id and supplier_company_id!=''):
            supplier_company = Company.objects.get(id=supplier_company_id)
            queryset = queryset.filter( supplier_company = supplier_company)

        if(search and search != ''):
            fields = [
            'supplier_name__icontains',
            'supplier_tax_number__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')

        return queryset

import time

@permission_classes([IsAuthenticated])
class TraceabilityFileExport(APIView):

    def _get_export_response(self, queryset, format='csv', language_code= 'en'):

        if language_code == 'es':
            dataset = TraceabilitySpanishExportResource().export(queryset)
        elif language_code == 'pt':
            dataset = TraceabilityPortugueseExportResource().export(queryset)
        else:
            dataset = TraceabilityEnglishExportResource().export(queryset)

        file_name = "Traceability_{}".format(dt.datetime.now().strftime("%d-%m-%Y"))

        if (format == 'csv'):
            dataset_format = dataset.csv
            CONTENT_DISPOSITION = 'attachment; filename="{}.csv"'.format(file_name)
            CONTENT_TYPE = 'text/csv'

        elif (format == 'xls'):
            dataset_format = dataset.xls
            CONTENT_DISPOSITION = 'attachment; filename="{}.xls"'.format(file_name)
            CONTENT_TYPE = 'application/vnd.ms-excel'

        elif (format == 'xlsx'):
            dataset_format = dataset.xlsx
            CONTENT_DISPOSITION = 'attachment; filename="{}.xlsx"'.format(file_name)
            CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        else:
            dataset_format = dataset.csv
            CONTENT_DISPOSITION = 'attachment; filename="_{}.csv"'.format(file_name)
            CONTENT_TYPE = 'text/csv'

        response = HttpResponse(dataset_format, content_type=CONTENT_TYPE)
        response['Content-Disposition'] = CONTENT_DISPOSITION
        return response

    def get(self, request, format=None):
        queryset = Traceability.objects.all()
        language_code = self.request.headers.get('Content-Language')    
        search = self.request.query_params.get('search')
        if self.request.user.role.name == 'CLIENTE': #Return just reported by my company
            queryset = Traceability.objects.filter(reported_company = self.request.user.company)

        year = self.request.query_params.get('year')
        period = self.request.query_params.get('period')

        if(search and search != ''):
            fields = [
            'supplier_name__icontains',
            'supplier_tax_number__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')
        
        if (year and year != ''):
            queryset = queryset.filter( year = year )

        if (period and period != ''):
            queryset = queryset.filter(period = period )
        
        format_file_available = {
            '0': 'csv',
            '1': 'xls',
            '2': 'xlsx'
            }
        format_file_id = request.GET.get('_format_file')
        try:
            format_file = format_file_available[format_file_id]
        except:
            format_file = format_file_available['0']

        
        if Check_user_in_groups(self.request.user, ['SUPERUSUARIO']):
            companies_count_initial = 0
            new_companies_count = 10
            while companies_count_initial < new_companies_count:
                #ARMO LA LISTA DE PROVEEDORES en ese query
                query_company_ids = queryset.values_list('supplier_company', flat=True).distinct()
                query_companies = Company.objects.filter(id__in=query_company_ids)
                companies_count_initial = query_companies.count()
                
                for supplier in query_companies:
                    
                    queryset_complementario = Traceability.objects.filter(reported_company = supplier)
                    if (year and year != ''):
                        queryset_complementario = queryset_complementario.filter( year = year )
                    if (period and period != ''):
                        queryset_complementario = queryset_complementario.filter(period = period )
                    queryset = queryset | queryset_complementario
                new_query_company_ids = queryset.values_list('supplier_company', flat=True).distinct()
                new_query_companies = Company.objects.filter(id__in=new_query_company_ids)
                new_companies_count = new_query_companies.count()
                
            
        response = self._get_export_response(queryset, format=format_file, language_code=language_code)
        return response

from rest_framework.response import Response


@permission_classes([IsAuthenticated])
class GetMyCompany(APIView):

    def get(self, request, format=None):

        if self.request.user.role.name == 'CLIENTE': #Return just reported by my company
            company = self.request.user.company
            response = {
            'id':company.id,
            'name_company' : company.name,
            'latitude': company.latitude,
            'longitude': company.longitude
            }
        else:
            # company = Company.objects.get(identifier_global_company='PROFORESTGLOBAL')
            response = {
                'id': 0,
                'name_company' : 'PROFORESTGLOBAL',
                'latitude': None,
                'longitude': None
            }

        return Response(response)


#Vista de trazabilidades para admin

@permission_classes([CustomDjangoModelPermission])
class TraceabilityColaboratorList(generics.ListAPIView):
    queryset = Traceability.objects.all()
    serializer_class = TraceabilityColaboratorSerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

    def get_queryset(self):
        queryset = Traceability.objects.all()
        id_company = self.request.query_params.get('id_company')
        year = self.request.query_params.get('year')
        period = self.request.query_params.get('period')
        search = self.request.query_params.get('search')

        pais = self.request.query_params.get('pais')
        region = self.request.query_params.get('region')
        ciudad = self.request.query_params.get('ciudad')

        commodity = self.request.query_params.get('commodity')
        tipo_actor = self.request.query_params.get('tipo_actor')

        company = Company.objects.get(id=id_company)
        queryset = Traceability.objects.filter(reported_company = company)

        if (year and year != ''):
            queryset = queryset.filter( year = year )

        if (period and period != ''):
            if period != '0': #si es diferente de cero busca un periodo en particular
                queryset = queryset.filter(period = period )

        if (pais  and pais !=''):
            queryset = queryset.filter(country__id=pais)

        if (region  and region !=''):
            queryset = queryset.filter(region__id=region)
        
        if (ciudad  and ciudad !=''):
            queryset = queryset.filter(city__id=ciudad)

        if (commodity and commodity!=''):
            queryset = queryset.filter(commodity__id = commodity)

        if (tipo_actor and commodity!=''):
            queryset = queryset.filter(actor_type__id = tipo_actor)

        if(search and search != ''):
            fields = [
            'supplier_name__icontains',
            'supplier_tax_number__icontains',
            'country__name__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')

        return queryset
    
    def list(self, request, *args, **kwargs):
        id_company = self.request.query_params.get('id_company')
        company = Company.objects.get(id=id_company)

        response = super().list(request, *args, **kwargs)
        response.data['company_data'] = {
            'id':company.id,
            'name_company' : company.name,
            'latitude': company.latitude,
            'longitude': company.longitude
        }

        return response

