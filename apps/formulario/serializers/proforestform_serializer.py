from rest_framework import serializers
from apps.proforestform.models.proforestform import ProforestForm, Period

class ProforestFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProforestForm
        fields = [ 'id', 'code_form', 'name' 
        ]

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = [ 'id', 'name', 'code' ]
