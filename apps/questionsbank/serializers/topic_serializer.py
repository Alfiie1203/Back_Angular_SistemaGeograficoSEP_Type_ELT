from rest_framework import serializers
from ..models.topic import Topic
from .subcategory_serializer import SubCategorySerializerNotCategory
from .category_serializer import CategorySerializer


class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(status=True)
        return super(FilteredListSerializer, self).to_representation(data)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name_en', 'name_es', 'name_pt', 'code', 'status', 'subcategory']

class TopicSerializerSimple(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Topic
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict

class TopicSerializerDetail(serializers.ModelSerializer):
    subcategory = SubCategorySerializerNotCategory(read_only=True)
    category = serializers.SerializerMethodField('get_category')
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Topic
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status', 'subcategory', 'category']

    def get_category(self, object):
        category = object.subcategory.category
        dict_category = {}
        dict_category["en"] = category.name_en
        dict_category["es"] = category.name_es
        dict_category["pt"] = category.name_pt
        dict = {}
        dict['id'] = category.id
        dict['name'] = dict_category
        dict['name_en'] = category.name_en
        dict['name_es'] = category.name_es
        dict['name_pt'] = category.name_pt
        dict['code'] = category.code
        dict['status'] = category.status

        return dict

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict


class TopicSerializerStatusTrue(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = Topic
        fields = ['id', 'name_en', 'name_es', 'name_pt', 'code', 'status']
