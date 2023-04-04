from rest_framework import serializers
#from .commodity_serializer import CommoditySerializer
from ..models.actor_type import ActorType
from ..models.commodity import Commodity


class SimpleCommoditySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Commodity
        fields = ['id', 'name', 'name_es', 'name_en', 'name_pt', 'proforest_commodity_code',
                  'status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict


class ActorTypeSerializerDetail(serializers.ModelSerializer):
    commodity = SimpleCommoditySerializer()
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = ActorType
        fields = ['id', 'name', 'name_es', 'name_en', 'name_pt', 'proforest_actortype_code',
                'is_productor',
                'status', 'commodity']
    
    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict


class ActorTypeSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = ActorType
        fields = ['id', 'name', 'name_es', 'name_en', 'name_pt', 'proforest_actortype_code', 'commodity',
                  'is_productor',
                  'status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict


class ActorTypeSerializerSimpleName(serializers.ModelSerializer):

    class Meta:
        model = ActorType
        fields = ['name']
