from apps.questionsbank.models.subcategory import SubCategory
from apps.questionsbank.models.topic import Topic
from apps.utils.permissions import CustomDjangoModelPermission
from ..models.category import Category
from ..serializers.category_serializer import CategorySerializer, CategorySerializerDetail

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q


# API views for Category

@permission_classes([CustomDjangoModelPermission])
class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
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
class CategoryCreate(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@permission_classes([IsAuthenticated])
class CategoryView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializerDetail

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@permission_classes([IsAuthenticated])
class CategoryUpdate(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_update(self, serializer,):
        status = serializer.validated_data['status']
        serializer.save()
        for subcategory in SubCategory.objects.filter(category=self.get_object()):
            subcategory.status = status
            subcategory.save()
            for topic in Topic.objects.filter(subcategory=subcategory):
                topic.status = status
                topic.save()
        


@permission_classes([IsAuthenticated])
class CategoryDestroy(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
                            "detail": "Category cannot be deleted it is asociated to other models.",
                            "attr": "Category"
                        }
                    ]
                },
                403
            )


@permission_classes([IsAuthenticated])
class CategorySearch(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get(self, request):
        language_code = self.request.headers.get('Content-Language')
        name_translate = 'name_'+ language_code
        search = self.request.GET.get('name')

        if search != None:
            fields = [
                f'name_{language_code}__icontains',
                'code__icontains',
            ]
            filters = Q()
            for str_field in fields:
                filters |= Q(**{str_field: search})
            queryset = Category.objects.filter(filters).order_by('id')[:5]
        
        else:
            queryset = Category.objects.all()[:10]

        array = []
        for category in queryset:
            array.append(getattr(category, name_translate))

        return Response({'results': array})
