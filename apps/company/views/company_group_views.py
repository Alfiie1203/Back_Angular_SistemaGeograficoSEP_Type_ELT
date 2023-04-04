from apps.utils.permissions import CustomDjangoModelPermission
from rest_framework.permissions import IsAuthenticated
from ..models.company_group import CompanyGroup
from ..serializers.company_group_serializer import CompanyGroupSerializer

from rest_framework import generics
from rest_framework import status

from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from django.db.models import Q


@permission_classes([IsAuthenticated])
class CompanyGroupList(generics.ListAPIView):
    serializer_class = CompanyGroupSerializer

    def check_permissions(self, request):
        """
        Check if the user has the necessary permissions to access the view.
        """
        if not (request.user.has_perm('company.add_company')  or request.user.has_perm('company.add_companygroup')):
            # If the user doesn't have the necessary permission, raise a PermissionDenied exception
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied({'message': 'You do not have permission to perform this action.'})

    def get_queryset(self):
        queryset = CompanyGroup.objects.all()
        status = self.request.GET.get('status')
        name = self.request.GET.get('name')
        active = self.request.GET.get('active')
        direction = self.request.GET.get('direction')
        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)
        if name != None:
            queryset = CompanyGroup.objects.filter(
                name__unaccent__icontains=name)
        if active:
            if direction == '':
                pass
            elif direction == 'asc':
                queryset = queryset.order_by(active)
            elif direction == 'desc':
                filter = str('-'+active)
                queryset = queryset.order_by(filter)
        return queryset


class CompanyGroupListCreateCompanyForm(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyGroupSerializer

    def check_permissions(self, request):
        """
        Check if the user has the necessary permissions to access the view.
        """
        if not (request.user.has_perm('company.add_company') or request.user.has_perm('company.change_company') or request.user.has_perm('company.update_own_company')):
            # If the user doesn't have the necessary permission, raise a PermissionDenied exception
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied({'message': 'You do not have permission to perform this action.'})

    
    def get_queryset(self):
        status = self.request.GET.get('status')
        queryset = CompanyGroup.objects.all()
        if status == 'false':
            queryset = queryset.filter(status=False)
        elif status == 'true':
            queryset = queryset.filter(status=True)
        return queryset


@permission_classes([CustomDjangoModelPermission])
class CompanyGroupCreate(generics.CreateAPIView):
    queryset = CompanyGroup.objects.all()
    serializer_class = CompanyGroupSerializer


@permission_classes([CustomDjangoModelPermission])
class CompanyGroupView(generics.RetrieveAPIView):
    queryset = CompanyGroup.objects.all()
    serializer_class = CompanyGroupSerializer


@permission_classes([CustomDjangoModelPermission])
class CompanyGroupUpdate(generics.UpdateAPIView):
    queryset = CompanyGroup.objects.all()
    serializer_class = CompanyGroupSerializer


@permission_classes([CustomDjangoModelPermission])
class CompanyGroupDestroy(generics.DestroyAPIView):
    queryset = CompanyGroup.objects.all()
    serializer_class = CompanyGroupSerializer

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
                            "detail": "CompanyGroup cannot be deleted it is asociated to other models.",
                            "attr": "CompanyGroup"
                        }
                    ]
                },
                403
            )


@permission_classes([IsAuthenticated])
class CompanyGroupSearch(generics.ListAPIView):
    serializer_class = CompanyGroupSerializer

    def get(self, request):
        name = self.request.GET.get('name')
        if name != None:
            queryset = CompanyGroup.objects.filter(
                Q(name__unaccent__icontains=name))[:5]
        else:
            queryset = CompanyGroup.objects.all()
        array = []
        for a in queryset:
            array.append(a.name)
        return Response({'results': array})
