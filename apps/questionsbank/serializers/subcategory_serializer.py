from rest_framework import serializers
from ..models.subcategory import SubCategory
from .category_serializer import CategorySerializer
from ..models.topic import Topic


class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(status=True)
        return super(FilteredListSerializer, self).to_representation(data)


class SubCategorySerializer(serializers.ModelSerializer):
    
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code','status', 'category']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict

class SubCategorySerializerNotCategory(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code','status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict


class SubCategorySerializerDetailCategory(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status', 'category']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict

class SubCategorySerializerStatusTrue(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        list_serializer_class = FilteredListSerializer
        model = SubCategory
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict

class SubCategorySerializerDetailTopic(serializers.ModelSerializer):
    
    from .topic_serializer import TopicSerializerStatusTrue

    topic = TopicSerializerStatusTrue(many=True, read_only=True)
    category = CategorySerializer(read_only=True)       

    class Meta:
        model = SubCategory
        fields = ['id', 'name_en', 'name_es', 'name_pt', 'code', 'status', 'category', 'topic']