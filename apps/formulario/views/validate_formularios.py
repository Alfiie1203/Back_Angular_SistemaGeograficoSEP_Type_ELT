from apps.emailcustom.models import EmailTemplate

from apps.utils.permissions import CustomDjangoModelPermission
from apps.user.models import User

from ..models.formulario import Formulario
from ..models.question import Question, QuestionHistory
from ..serializers.formulario_serializer import FormularioSerializer, FormularioAsignSerializer, FormularioCreateSerializer, FormularioDetailSerializer, FormularioSerializerList, FormularioUpdateSerializer

from datetime import datetime as dt

from rest_framework import generics
from rest_framework import serializers

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@permission_classes([CustomDjangoModelPermission])
class ValidateListFormularios(generics.ListAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializerList
    def get_queryset(self):
        queryset = Formulario.objects.all()
        revision_status = self.request.GET.get('revision_status')
        proforestform_id = self.request.GET.get('proforestform_id')
        revisor_user_id = self.request.GET.get('revisor_id')
        period = self.request.GET.get('period')
        name = self.request.GET.get('name') #assigned_company_name
        
        if proforestform_id:
            queryset = queryset.filter(proforestform__id = proforestform_id)
        if period:
            queryset = queryset.filter(period__id = period)
        if name:
            queryset = queryset.filter(assigned_company__name__icontains = name)
        if revision_status:
            queryset = queryset.filter(revision_status = revision_status)
        if revisor_user_id == '' :
            pass
        elif revisor_user_id == 0 or revisor_user_id == None :
            queryset = queryset.filter(revisor = None)
        else:
            queryset = queryset.filter(revisor = User.objects.get(id = revisor_user_id))

        return queryset

@permission_classes([IsAuthenticated])
class AssignValidateListFormularios(APIView):
    def post(self, request): 
        queryset = Formulario.objects.all()
        revision_status = request.data['revision_status']
        proforestform = request.data['proforestform_id']
        revisor_user_id = request.data['revisor_id']
        period = request.data['period']
        name = request.data['name'] #assigned_company_name

        usuarios_asignados = request.data['assigned_validator_id']
        start_date_validation = request.data['start_date_validation']
        end_date_validation =request.data['end_date_validation']

        start_date_validation = dt.strptime(request.data['start_date_validation'], "%Y-%m-%d").date()
        end_date_validation = dt.strptime(request.data['end_date_validation'], "%Y-%m-%d").date()
        today = dt.now().date()
        if (start_date_validation >= today) and (end_date_validation > today) :
            pass # The date is in the future 
        else:
            return Response(
                {
                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "assigned_dates",
                            "detail": "Assigned dates must not be less than today",
                            "attr": "Assigned Dates"
                        }
                    ]
                },
                403
            )
        
        if proforestform:
            queryset = queryset.filter(proforestform = proforestform)
        if period:
            queryset = queryset.filter(period__id = period)
        if name:
            queryset = queryset.filter(assigned_company__name__icontains = name)
        if revision_status:
            queryset = queryset.filter(revision_status = revision_status)
        if revisor_user_id == '' :
            pass
        elif revisor_user_id == 0 or revisor_user_id == None :
            queryset = queryset.filter(revisor = None)
        else:
            queryset = queryset.filter(revisor = User.objects.get(id = revisor_user_id))


        total_mod = queryset.count()
        queryset.update(start_date_validation= start_date_validation, end_date_validation = end_date_validation,
                revision_status = 'WITHOUTVALIDATE',
                )
        for formulario in queryset:
            formulario.revisor.set(usuarios_asignados, clear= True)
            formulario.save()

        return Response({'results': 'Forms asigned to validator', 'asignado': total_mod})
    
@permission_classes([IsAuthenticated])
class FormularioAssignValidators(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioUpdateSerializer

    def perform_update(self, serializer):

        start_date_validation = dt.strptime(self.request.data['start_date_validation'], "%Y-%m-%d").date()
        end_date_validation = dt.strptime(self.request.data['end_date_validation'], "%Y-%m-%d").date()
        today = dt.now().date()
        if (start_date_validation >= today) and (end_date_validation > today) :
            serializer.save(
                # status_revision = 'NV',
            )
            

        else:
            raise serializers.ValidationError("Assigned dates must not be less than today")