from ..models.traceability import Traceability
from apps.cities.serializers import CountriesSerializer, RegionsSerializer, SubRegionsSerializer
from apps.company.serializers.commodity_serializer import CommoditySerializer
from apps.company.serializers.actor_type_serializer import ActorTypeSerializer
from apps.company.serializers.company_group_serializer import CompanyGroupSerializer

from rest_framework import serializers

class TraceabilitySerializer(serializers.ModelSerializer):
    reported_company_nit = serializers.ReadOnlyField(source= 'reported_company.nit')
    supplier_company_id = serializers.ReadOnlyField(source='supplier_company.id')
    supplier_company = serializers.ReadOnlyField(source='supplier_company.name')
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    company_group = CompanyGroupSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)
    reported_user = serializers.ReadOnlyField(source='reported_user.get_full_name')
    reported_company = serializers.ReadOnlyField(source='reported_company.name')

    class Meta:
        model = Traceability
        fields = ( 'id', 'reported_user', 'reported_company',
                'reported_company_nit',
                'supplier_company_id',
                'supplier_company',
                'supplier_name',
                'commodity', 'actor_type', 'company_group',
                'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'certification', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period',
                'date_reported',
                'status_revision',
                
        )
    def get_commodity_translate_name(self, obj):
        language_code = 'name_'+ self.context["language_code"]
        return getattr(obj.commodity, language_code)

    def get_actortype_translate_name(self, obj):
        language_code = 'name_'+ self.context["language_code"]
        return getattr(obj.actor_type, language_code)


class TraceabilityCreateSerializer(serializers.ModelSerializer):


    class Meta:
        model = Traceability
        fields = ( 'id', 'commodity', 'actor_type', 'company_group',
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'certification', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period'
        )


class TraceabilityUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Traceability
        fields = ( 
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'latitude', 'longitude',
                'certification',
                'country', 'region', 'city', 'year', 'period',
                'status_revision',
        )


class TraceabilityColaboratorSerializer(serializers.ModelSerializer):

    supplier_company = serializers.ReadOnlyField(source='supplier_company.name')
    supplier_company = serializers.ReadOnlyField(source='supplier_company.id')
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    company_group = CompanyGroupSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)
    reported_user = serializers.ReadOnlyField(source='reported_user.get_full_name')
    reported_company = serializers.ReadOnlyField(source='reported_company.name')

    class Meta:
        model = Traceability
        fields = ( 'id', 'reported_user', 'reported_company', 'supplier_company', 'supplier_company_id', 'commodity', 'actor_type', 'company_group',
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'certification', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period',
                'date_reported',
                'status_revision',
                
        )
    def get_commodity_translate_name(self, obj):
        language_code = 'name_'+ self.context["language_code"]
        return getattr(obj.commodity, language_code)

    def get_actortype_translate_name(self, obj):
        language_code = 'name_'+ self.context["language_code"]
        return getattr(obj.actor_type, language_code)