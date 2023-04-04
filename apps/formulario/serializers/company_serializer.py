
from rest_framework import serializers
from apps.company.models.company import Company
from ..models.formulario import Formulario



class CompanySerializerList(serializers.ModelSerializer):

    supply_base = serializers.SerializerMethodField('get_suply_base_info')
    class Meta:
        model = Company
        fields = ['id', 'name', 'supply_base',
            # 'country', 'region', 'city', 'latitude', 'longitude', 'validator_user',
            ]

    def get_suply_base_info(self, obj):
        id_proforestform = self.context["id_proforest_form"]
        if id_proforestform == 'all_companies':
            return False
        elif Formulario.objects.filter(proforestform__id= id_proforestform, assigned_company = obj).exists():
            return True
        return False

class CompanySerializerListSimple(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['id', 'name', 
            ]
