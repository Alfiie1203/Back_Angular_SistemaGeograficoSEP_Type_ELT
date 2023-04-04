from rest_framework import serializers


from apps.company.models.company import Company
from apps.company.serializers.commodity_serializer import CommoditySerializer
from apps.company.serializers.actor_type_serializer import ActorTypeSerializer
from apps.cities.serializers import CountriesSerializer, RegionsSerializer, SubRegionsSerializer
from apps.traceability.models.traceability import Traceability
from apps.user.models import User


class CompanySerializerView(serializers.ModelSerializer):
    commodity = CommoditySerializer(read_only=True)
    actor_type = ActorTypeSerializer(read_only=True)
    validator_user = serializers.ReadOnlyField(source='validator_user.get_full_name')
    country = CountriesSerializer(read_only=True)
    region = RegionsSerializer(read_only=True)
    city = SubRegionsSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ['id',
                    'name',
                    'nit',
                    'status_revision',
                    'validator_user',
                    'commodity', 'actor_type',
                    'country', 'region', 'city',
                    'latitude', 'longitude',
                    'note_revision',
                    'start_date_validation',
                    'end_date_validation',
                    ]



class CompanySerializerEdit(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['id',
                    'name',
                    'status_revision',
                    'validator_user',
                    'commodity', 'actor_type', 
                    'note_revision',
                    'country', 'region', 'city',
                    'latitude', 'longitude',
                    'note_revision',
                    'start_date_validation',
                    'end_date_validation',

                    ]

class CompanyResumeValidationSerializer(serializers.ModelSerializer):
    name_company = serializers.ReadOnlyField(source='name')
    porcentaje_validadas = serializers.SerializerMethodField('get_porcentaje_validadas')

    class Meta:
        model = Company
        fields = [  'id',
                    'name_company',
                    'porcentaje_validadas',

                    ]

    def get_porcentaje_validadas(self, obj):
        user_pk = self.context["user_pk"]
        if user_pk:
            traceabilitys_query = Traceability.objects.filter(validator_user = User.objects.get(id=user_pk), reported_company = obj).exclude(status_revision='VE').exclude(status_revision='NVE')
        else:
            traceabilitys_query = Traceability.objects.filter(reported_company = obj)


        period = self.context["period"]
        year = self.context["year"]

        if period and period!= '0':
            traceabilitys_query = traceabilitys_query.filter(period=period)
        if year and year!='':
            traceabilitys_query = traceabilitys_query.filter(year= year)

        try:
            return round(((traceabilitys_query.filter(status_revision='VA').count())*100)/traceabilitys_query.count())
        except:
            return 0

class CompanyResumeVerificationSerializer(serializers.ModelSerializer):
    name_company = serializers.ReadOnlyField(source='name')
    porcentaje_validadas = serializers.SerializerMethodField('get_porcentaje_validadas')

    class Meta:
        model = Company
        fields = [  'id',
                    'name_company',
                    'porcentaje_validadas',

                    ]

    def get_porcentaje_validadas(self, obj):
        user_pk = self.context["user_pk"]
        if user_pk:
            traceabilitys_query = Traceability.objects.filter(validator_user = User.objects.get(id=user_pk), reported_company = obj)
        else:
            traceabilitys_query = Traceability.objects.filter(reported_company = obj)


        period = self.context["period"]
        year = self.context["year"]

        if period and period!= '0':
            traceabilitys_query = traceabilitys_query.filter(period=period)
        if year and year!='':
            traceabilitys_query = traceabilitys_query.filter(year= year)

        try:
            return round((traceabilitys_query.filter(status_revision='VE').count()*100)/traceabilitys_query.count())
        except:
            return 0
