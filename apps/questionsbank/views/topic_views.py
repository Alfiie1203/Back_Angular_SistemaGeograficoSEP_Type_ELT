from apps.questionsbank.models.category import Category
from apps.questionsbank.models.subcategory import SubCategory
from apps.utils.permissions import CustomDjangoModelPermission
from ..models.topic import Topic
from ..serializers.topic_serializer import TopicSerializer, TopicSerializerDetail, TopicSerializerSimple

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q


# API views for Topic

@permission_classes([IsAuthenticated])
class TopicList(generics.ListAPIView):
    serializer_class = TopicSerializerDetail

    def get_queryset(self):
        queryset = Topic.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')
        language_code = self.request.headers.get('Content-Language')

        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)
        if search != None:
            fields = [
                f'name_{language_code}__unaccent__icontains',
                'code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')

        if active:
            if direction == '':
                pass
            elif direction == 'asc':
                queryset = queryset.order_by(active)
            elif direction == 'desc':
                filter = str('-'+active)
                queryset = queryset.order_by(filter)
        return queryset

@permission_classes([IsAuthenticated])
class TopicListSimple(generics.ListAPIView):
    serializer_class = TopicSerializerSimple

    def get_queryset(self):
        queryset = Topic.objects.all()
        status = self.request.GET.get('status')
        search = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')
        category_pk = self.request.GET.get('category')
        subcategory_pk = self.request.GET.get('subcategory')
        language_code = self.request.headers.get('Content-Language')


        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)
        if search != None:
            fields = [
                f'name_{language_code}__unaccent__icontains',
                'code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = queryset.filter(filters).order_by('id')
        if category_pk:
            category = Category.objects.get(pk=category_pk)
            queryset = queryset.filter(subcategory__category = category)
        if subcategory_pk:
            subcategory = SubCategory.objects.get(pk=subcategory_pk)
            queryset = queryset.filter(subcategory = subcategory)
        if active:
            if direction == '':
                pass
            elif direction == 'asc':
                queryset = queryset.order_by(active)
            elif direction == 'desc':
                filter = str('-'+active)
                queryset = queryset.order_by(filter)
        return queryset


@permission_classes([IsAuthenticated])
class TopicCreate(generics.CreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


@permission_classes([IsAuthenticated])
class TopicView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializerDetail


@permission_classes([IsAuthenticated])
class TopicUpdate(generics.UpdateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    def update(self, request, *args, **kwargs):
        actual = Topic.objects.get(id=request.data.get('id'))
        subcategoria = SubCategory.objects.get(id = actual.subcategory.id)
        if subcategoria.status == False :
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "Topic cannot be update it is associated to disabled Subcategory.",
                            "attr": "Topic"
                        }
                    ]
                },
                403
            )
        return super().update(request, *args, **kwargs)


@permission_classes([CustomDjangoModelPermission])
class TopicDestroy(generics.DestroyAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "Topic cannot be delete it is associated to other models",
                            "attr": "Topic"
                        }
                    ]
                },
                403
                
            )

@permission_classes([IsAuthenticated])
class TopicSearch(generics.ListAPIView):
    serializer_class = TopicSerializer

    def get(self, request):
        search = self.request.GET.get('name')
        if search != None:
            fields = [
                'name_es__icontains',
                'name_en__icontains',
                'name_pt__icontains',
                'code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = Topic.objects.filter(filters).order_by('id')[:5]
        
        else:
            queryset = Topic.objects.all()[:5]

        array = []
        for topic in queryset:
            array.append(getattr(topic, 'name_en'))
            array.append(getattr(topic, 'name_es'))
            array.append(getattr(topic, 'name_pt'))

        return Response({'results': array})


