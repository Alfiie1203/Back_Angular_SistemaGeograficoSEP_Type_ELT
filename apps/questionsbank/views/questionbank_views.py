from apps.utils.permissions import CustomDjangoModelPermission
from django.views.generic import ListView

from ..models.questionbank import QuestionBank
from ..serializers.questionbank_serializer import QuestionBankSerializer, QuestionBankSerializerDetail

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import JsonResponse
from django.db.models.expressions import RawSQL



# API views for QuestionBank

@permission_classes([CustomDjangoModelPermission])
class QuestionBankList(generics.ListAPIView):
    serializer_class = QuestionBankSerializer

    def get_queryset(self):
        queryset = QuestionBank.objects.all().order_by(RawSQL("question_data->>%s", ("label",)))
        category = self.request.GET.get('category')
        subcategory = self.request.GET.get('subcategory')
        topic = self.request.GET.get('topic')

       
        if category:
            queryset = queryset.filter(category__id = category)
        if subcategory:
            queryset = queryset.filter(subcategory__id = subcategory)
        if topic:
            queryset = queryset.filter(topic__id = topic)
        return queryset


@permission_classes([IsAuthenticated])
class QuestionBankCreate(generics.CreateAPIView):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer


@permission_classes([IsAuthenticated])
class QuestionBankView(generics.RetrieveAPIView):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer


@permission_classes([IsAuthenticated])
class QuestionBankUpdate(generics.UpdateAPIView):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer

    def update(self, request, *args, **kwargs):

        questionbank_actual = QuestionBank.objects.get(id=request.data.get('id'))
        if questionbank_actual.category.status == False :
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "Question cannot be update it is associated to disabled Category.",
                            "attr": "Question-Category"
                        }
                    ]
                },
                403
            )
        if questionbank_actual.subcategory.status == False :
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "Question cannot be update it is associated to disabled Sub-Category.",
                            "attr": "Question-SubCategory"
                        }
                    ]
                },
                403
            )
        if questionbank_actual.topic.status == False :
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "Question cannot be update it is associated to disabled Topic.",
                            "attr": "Question-Topic"
                        }
                    ]
                },
                403
            )
        return super().update(request, *args, **kwargs)


@permission_classes([IsAuthenticated])
class QuestionBankDestroy(generics.DestroyAPIView):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = self.perform_destroy(instance)
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_destroy",
                            "detail": "QuestionBank cannot be deleted it is asociated to other models.",
                            "attr": "QuestionBank"
                        }
                    ]
                },
                403
            )



@permission_classes([IsAuthenticated])
class QuestionBankView(generics.RetrieveAPIView):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializerDetail



# Temporal for test render of questions on backoffice 
class JavascriptView(ListView):
    template_name = 'index.html'
    url_name = 'javascript-list'
    model = QuestionBank
    paginate_by = 25

def django_models_json(request):
    if request.method == 'POST':
        question_bank = QuestionBank.objects.get(pk =request.POST['question_pk'])
        serializer = QuestionBankSerializer(question_bank)
        return JsonResponse(serializer.data, safe = False)

