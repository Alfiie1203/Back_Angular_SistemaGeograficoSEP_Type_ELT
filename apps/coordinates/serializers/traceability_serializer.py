from apps.traceability.models.traceability import Traceability
from apps.cities.serializers import CountriesSerializer, RegionsSerializer, SubRegionsSerializer
from apps.company.serializers.commodity_serializer import CommoditySerializer
from apps.company.serializers.actor_type_serializer import ActorTypeSerializer
from apps.company.serializers.company_group_serializer import CompanyGroupSerializer

from rest_framework import serializers

from datetime import datetime as dt


class TraceabilityUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Traceability
        fields = ( 
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period',
                
        )

class TraceabilityValidateSerializer(serializers.ModelSerializer):

    supplier_company = serializers.ReadOnlyField(source='supplier_company.name')
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    company_group = CompanyGroupSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)
    reported_user = serializers.ReadOnlyField(source='reported_user.get_full_name')
    reported_company = serializers.ReadOnlyField(source='reported_company.name')
    validator_user =  serializers.ReadOnlyField(source='validator_user.get_full_name')
    can_update = serializers.SerializerMethodField('get_can_update')

    class Meta:
        model = Traceability
        fields = ( 'id', 'reported_user', 'reported_company', 'supplier_company', 'commodity', 'actor_type', 'company_group',
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'certification', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period',
                # 'date_reported',
                'status_revision',
                'start_date_validation',
                'end_date_validation',
                'validator_user',
                'can_update',

        )

    def get_can_update(self, obj):
        today = dt.now().date()
        try:
            if obj.start_date_validation <= today <= obj.end_date_validation :
                return True
            else:
                return False
        except:
            return True
    

class TraceabilityVerifySerializer(serializers.ModelSerializer):

    supplier_company = serializers.ReadOnlyField(source='supplier_company.name')
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    company_group = CompanyGroupSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)
    reported_user = serializers.ReadOnlyField(source='reported_user.get_full_name')
    reported_company = serializers.ReadOnlyField(source='reported_company.name')
    validator_user = serializers.ReadOnlyField(source='validator_user.get_full_name')
    can_update = serializers.SerializerMethodField('getcan_update')

    class Meta:
        model = Traceability
        fields = ( 'id', 'reported_user', 'reported_company', 'supplier_company', 'commodity', 'actor_type', 'company_group',
                'supplier_name', 'supplier_tax_number', 'supplier_capacity', 'supplier_production', 
                'purchased_volume', 'certification', 'latitude', 'longitude',
                'country', 'region', 'city', 'year', 'period',
                # 'date_reported',
                'status_revision',
                'start_date_validation',
                'end_date_validation',
                'validator_user',
                'can_update',
        )

    def getcan_update(self, obj):
        today = dt.now().date()
        try:
            if obj.start_date_validation <= today <= obj.end_date_validation:
                return True
            else:
                return False
        except: #Si no tiene fechas pues no deberia dejarse actualizar
            return True

