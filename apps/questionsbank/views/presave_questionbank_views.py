from apps.questionsbank.models.category import Category
from apps.questionsbank.models.subcategory import SubCategory
from apps.questionsbank.models.topic import Topic
from ..models.questionbank import QuestionBank

from rest_framework.views import APIView
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json



@permission_classes([IsAuthenticated])
class QuestionSave(APIView):
    
    def post(self, request):
        dictionary = self.request.data
        json_data = dictionary['data']
        id_category = dictionary['category']
        id_subcategory = dictionary['subcategory']
        id_topic = dictionary['topic']
        question_id = dictionary['id'] if 'id' in dictionary.keys() else None
        
        if question_id == None:
            newquestion = QuestionBank.objects.create(
                category = Category.objects.get(pk=id_category),
                subcategory = SubCategory.objects.get(pk=id_subcategory),
                topic = Topic.objects.get(pk=id_topic),
                question_data = json_data
            )
            return Response({'info': 'new_question_created', 'id_question': newquestion.pk })
        else:
            old_question = QuestionBank.objects.get(pk=question_id)
            for key in json_data:
                old_question.question_data[key] = json_data[key]
                old_question.save()

            return Response({'info': 'question_updated', 'id_question': question_id, 'data': old_question.question_data })