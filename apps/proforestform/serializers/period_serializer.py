from rest_framework import serializers
from ..models.proforestform import Period

class PeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Period
        fields = ['id', 'name', 'code', 'months']