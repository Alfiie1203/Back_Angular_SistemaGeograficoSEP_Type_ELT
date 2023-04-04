from cities_light.models import Country, Region, SubRegion

from rest_framework import serializers


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'slug',
            'phone'
        )
        model = Country


class RegionsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'display_name',
            'slug',
        )
        model = Region


class SubRegionsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'display_name',
            'slug',
        )
        model = SubRegion
