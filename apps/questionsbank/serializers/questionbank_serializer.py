from rest_framework import serializers
from ..models.questionbank import QuestionBank
from ..serializers.category_serializer import CategorySerializer
from ..serializers.subcategory_serializer import SubCategorySerializerNotCategory
from ..serializers.topic_serializer import TopicSerializerSimple

class QuestionBankSerializerDetail(serializers.ModelSerializer):

    category = CategorySerializer()
    subcategory = SubCategorySerializerNotCategory()
    topic = TopicSerializerSimple()
    class Meta:
        model = QuestionBank
        fields = [ 'id', 'status', 'category','subcategory','topic','question_data']


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['id', 'category', 'subcategory', 'topic', 'question_data', 'status']