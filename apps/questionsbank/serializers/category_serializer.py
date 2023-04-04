
from rest_framework import serializers
from ..models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Category
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict
    


class CategorySerializerDetail(serializers.ModelSerializer):

    from .subcategory_serializer import SubCategorySerializerStatusTrue  # Prevent ImportCycle

    subcategory = SubCategorySerializerStatusTrue(many=True, read_only=True)
    name = serializers.SerializerMethodField('get_translate_name')

    class Meta:
        model = Category
        fields = ['id', 'name', 'name_en', 'name_es', 'name_pt', 'code', 'status', 'subcategory']

    def get_translate_name(self, obj):
        dict = {}
        dict["en"] = obj.name_en
        dict["es"] = obj.name_es
        dict["pt"] = obj.name_pt
        return dict