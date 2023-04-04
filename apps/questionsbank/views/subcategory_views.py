from apps.utils.permissions import CustomDjangoModelPermission
from ..models.category import Category
from ..models.subcategory import SubCategory
from apps.questionsbank.models.topic import Topic
from ..serializers.subcategory_serializer import SubCategorySerializer, SubCategorySerializerDetailCategory, SubCategorySerializerDetailTopic

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q


# API views for SubCategory

@permission_classes([CustomDjangoModelPermission])
class SubCategoryList(generics.ListAPIView):
    serializer_class = SubCategorySerializerDetailCategory

    def get_queryset(self):
        queryset = SubCategory.objects.all()
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


@permission_classes([CustomDjangoModelPermission])
class SubCategoryCreate(generics.CreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


@permission_classes([CustomDjangoModelPermission])
class SubCategoryView(generics.RetrieveAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializerDetailTopic


@permission_classes([CustomDjangoModelPermission])
class SubCategoryUpdate(generics.UpdateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def update(self, request, *args, **kwargs):
        subcategory_actual = SubCategory.objects.get(id=request.data.get('id'))
        categoria = Category.objects.get(id = subcategory_actual.category.id)
        if categoria.status == False:
            return Response(
                {

                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "forbidden_update",
                            "detail": "SubCategory cannot be update it is associated to disabled Category.",
                            "attr": "Category"
                        }
                    ]
                },
                403
            )
        return super().update(request, *args, **kwargs)

@permission_classes([CustomDjangoModelPermission])
class SubCategoryDestroy(generics.DestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

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
                            "detail": "SubCategory cannot be deleted it is associated to other models.",
                            "attr": "SubCategory"
                        }
                    ]
                },
                403
            )


@permission_classes([IsAuthenticated])
class SubCategorySearch(generics.ListAPIView):
    serializer_class = SubCategorySerializer

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
            queryset = SubCategory.objects.filter(filters).order_by('id')[:5]
        
        else:
            queryset = SubCategory.objects.all()[:5]

        array = []
        for subcategory in queryset:
            array.append(getattr(subcategory, 'name_en'))
            array.append(getattr(subcategory, 'name_es'))
            array.append(getattr(subcategory, 'name_pt'))

        return Response({'results': array})


