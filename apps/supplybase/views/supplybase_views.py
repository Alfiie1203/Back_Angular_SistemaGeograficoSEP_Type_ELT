from apps.company.models.actor_type import ActorType
from apps.company.models.commodity import Commodity
from apps.company.models.company import Company
from apps.traceability.models.traceability import Traceability
from apps.utils.permissions import CustomDjangoModelPermission

from ..models.supplybase import SupplyBaseRegister, SupplyBaseDependency, PurchasedPercentage

from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user.views.groups import Check_user_in_groups


from ..serializers.supplybaseregister_serializer import (SupplyBaseRegisterListSerializer,
                SupplyBaseDependencySerializer, SupplyBaseRegisterCreateSerializer,
                SupplyBaseRegisterDetailSerializer, SupplyBaseTotalResumeSerializer,
                TraceabilityCompanyResumeSerializer, PurchasedPercentageSerializer
                )


@permission_classes([CustomDjangoModelPermission])
class SupplyBaseRegisterList(generics.ListAPIView):
    serializer_class = SupplyBaseRegisterListSerializer

    def get_queryset(self):
        if self.request.user.role.name=='COLABORADOR':
            queryset = SupplyBaseRegister.objects.all()
        else:
            queryset = SupplyBaseRegister.objects.filter(company=self.request.user.company)

        search = self.request.GET.get('search')
        year = self.request.GET.get('year')
        period = self.request.GET.get('period')

        if search != '' and search != None:
            queryset = queryset.filter(company__name__icontains = search)
        if year != '' and year != None:
            queryset = queryset.filter(register_year = year)
        if period != '' and period != None:
            queryset = queryset.filter(period = period)
        
        return queryset

@permission_classes([IsAuthenticated])
class SupplyBaseGetDependency(generics.ListAPIView):
    serializer_class = SupplyBaseDependencySerializer
    queryset = SupplyBaseDependency.objects.all()

    def get_queryset(self):
        company_id = self.request.GET.get('company_id')
        company = Company.objects.get(id= company_id)
        actor_type = company.actor_type
        return SupplyBaseDependency.objects.filter(actor_type = actor_type)


@permission_classes([IsAuthenticated])
class CheckSupplyBaseRegister(APIView):
    def get(self, request, format=None):
        """
        Return if exist previous registers.
        """
        company_id = self.request.GET.get('company_id')
        register_year = self.request.GET.get('register_year')
        period = self.request.GET.get('period')

        if  period == '0':
            if SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year).exists():
                supplyregister = SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year)[0]
                return Response({"exist": True, "register_by": supplyregister.created_by.email })
            else:
                return Response({"exist": False})
        if  period == '1':
            if (SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year, period=0).exists()) or (SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year, period=1).exists()):
                supplyregister = SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year)[0]
                return Response({"exist": True, "register_by": supplyregister.created_by.email })
            else:
                return Response({"exist": False})
        if  period == '2':
            if (SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year, period=0).exists()) or (SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year, period=2).exists()):
                supplyregister = SupplyBaseRegister.objects.filter(company__id=company_id, register_year=register_year)[0]
                return Response({"exist": True, "register_by": supplyregister.created_by.email })
            else:
                return Response({"exist": False})            
            

@permission_classes([IsAuthenticated])
class SupplyBaseCreate(generics.CreateAPIView):
    queryset = SupplyBaseRegister.objects.all()
    serializer_class = SupplyBaseRegisterCreateSerializer

    def perform_create (self, serializer):
        data = self.request.data
        user = self.request.user
        supplybaseregister = serializer.save(
            created_by = user,
            company = Company.objects.get(id=data['company'])
        )
        actor_type_dependency = data['actor_type_dependency']
        for register in actor_type_dependency:
            purchased_volume = round(float(register['percentage'])/100, 5)
            PurchasedPercentage.objects.create(
                supplybase_register = supplybaseregister,
                percentage = purchased_volume,
                actor_type = ActorType.objects.get(id=register['actor_type'])
            )

@permission_classes([IsAuthenticated])
class SupplyBaseDetailView(generics.RetrieveAPIView):
    queryset = SupplyBaseRegister.objects.all()
    serializer_class = SupplyBaseRegisterDetailSerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

#Obtain Supply base by period of a Company

from rest_framework.exceptions import NotFound 


@permission_classes([IsAuthenticated])
class ObtainSupplyBaseRegistersLocation(generics.ListAPIView):
    serializer_class = TraceabilityCompanyResumeSerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context


    def get_queryset(self):
        queryset = Traceability.objects.all()
        company_id = self.request.GET.get('company_id')
        year = self.request.GET.get('year')
        period = self.request.GET.get('period')

        groups_admin = ['SUPERADMINISTRADOR', 'ADMINISTRADOR', 'SUPERUSUARIO']
        if Check_user_in_groups(self.request.user, groups_admin):
            if Traceability.objects.filter(reported_company__id=company_id, year=year, period=period).exists():
                queryset = Traceability.objects.filter(reported_company__id=company_id, 
                                                        year=year, period=period)
                return queryset
            else:
                raise NotFound
        else:
            raise NotFound

    
@permission_classes([IsAuthenticated])
class SupplyBaseTotalResumeView(generics.RetrieveAPIView):
    queryset = SupplyBaseRegister.objects.all()
    serializer_class = SupplyBaseTotalResumeSerializer

    def get_serializer_context(self):
        language_code = self.request.headers.get('Content-Language')    
        context = super().get_serializer_context()
        context["language_code"] = language_code
        return context

#Obtain Supply base by period of a Company

@permission_classes([IsAuthenticated])
class PurchasedPercentageUpdateView(generics.UpdateAPIView):
    queryset = PurchasedPercentage.objects.all()
    serializer_class = PurchasedPercentageSerializer

    
