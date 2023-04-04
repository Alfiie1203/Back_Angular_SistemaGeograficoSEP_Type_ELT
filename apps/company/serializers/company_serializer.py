from rest_framework import serializers

from apps.cities.serializers import CountriesSerializer, RegionsSerializer, SubRegionsSerializer
from ..models.company import Company
from .commodity_serializer import CommoditySerializer
from .actor_type_serializer import ActorTypeSerializer
from .company_group_serializer import CompanyGroupSerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['identifier_proforest_company', 'id', 'name', 'country', 'region', 'city', 'latitude', 'longitude', 'identifier_global_company',
                  'nit', 'commodity', 'actor_type', 'company_group', 'validator_user', 'company_profile', 'status_revision', 'status']


class CompanySerializerDetail(serializers.ModelSerializer):
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    company_group = CompanyGroupSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ['identifier_proforest_company', 'id', 'name', 'country', 'region', 'city', 'latitude', 'longitude', 'identifier_global_company',
                  'nit', 'commodity', 'actor_type', 'company_group', 'validator_user', 'company_profile', 'status_revision', 'status']

class CompanySerializerReview(serializers.ModelSerializer):
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ['name', 'country', 'region', 'city', 'latitude', 'longitude',
                  'validator_user', 'company_profile', 'status_revision',
                  'commodity', 'actor_type', 'deadline_validation']

