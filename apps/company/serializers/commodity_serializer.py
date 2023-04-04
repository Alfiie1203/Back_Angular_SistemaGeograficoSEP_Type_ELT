from rest_framework import serializers
from .actor_type_serializer import ActorTypeSerializer
from ..models.commodity import Commodity
from ..models.actor_type import ActorType


class CommoditySerializer(serializers.ModelSerializer):
    
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

class CommoditySerializerDetail(serializers.ModelSerializer):

    actor_type = serializers.SerializerMethodField('get_active_list_actors')
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Commodity
        fields = ['id', 'name', 'name_es', 'name_en', 'name_pt', 'proforest_commodity_code',
                  'status', 'actor_type']

    def get_active_list_actors(self, obj):
        array = []
        actor_type_list = ActorType.objects.filter(commodity=obj, status=True)
        for actor in actor_type_list:
            dict_actor = {}
            dict_actor["en"] = actor.name_en
            dict_actor["es"] = actor.name_es
            dict_actor["pt"] = actor.name_pt
            dict = {}
            dict['id'] = actor.id
            dict['name'] = dict_actor
            dict['name_en'] =   actor.name_en
            dict['name_es'] = actor.name_es
            dict['name_pt'] = actor.name_pt
            dict['proforest_actortype_code'] = actor.proforest_actortype_code
            dict['commodity'] = actor.commodity.pk
            dict['status'] = actor.status
            array.append(dict)
        return array

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict