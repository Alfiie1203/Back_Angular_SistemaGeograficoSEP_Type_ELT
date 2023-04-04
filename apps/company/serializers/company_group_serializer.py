from rest_framework import serializers
from ..models.company_group import CompanyGroup

class CompanyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGroup
        fields = ['id', 'name', 'status']