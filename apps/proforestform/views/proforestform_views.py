from apps.utils.permissions import CustomDjangoModelPermission
from apps.formulario.models.formulario import Formulario
from apps.user.views.groups import Check_user_in_groups


from ..models.proforestform import ProforestForm, ProforestFormCode, Period

from ..serializers.proforestform_serializer import ( ProforestFormSerializer,
                    ProforestFormUpdateSerializer, ProforestFormDetailBankSerializer, ProforestFormSerializerList,
                    ProforestFormDetailSerializer)

from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q

import datetime as dt


# =============================================================================
#                           APIREST PROFOREST FORM RESOURCE
# =============================================================================

@permission_classes([CustomDjangoModelPermission])
class ProforestFormList(generics.ListAPIView):
    serializer_class = ProforestFormSerializerList

    def get_queryset(self):
        name = self.request.GET.get('name')
        period_id = self.request.GET.get('period_id')

        # revision_status = self.request.GET.get('revision_status')

        if Check_user_in_groups(self.request.user, ['SUPERADMINISTRADOR']):
            queryset = ProforestForm.objects.all()
        elif Check_user_in_groups(self.request.user, ['ADMINISTRADOR']):
            queryset1 = ProforestForm.objects.filter(collaborators = self.request.user)
            queryset2 = ProforestForm.objects.filter(created_by = self.request.user)
            queryset = queryset1.union(queryset2)

        elif (Check_user_in_groups(self.request.user, ['VERIFICADOR'])) or (Check_user_in_groups(self.request.user, ['VALIDADOR'])):
            formularios = Formulario.objects.filter(revisor = self.request.user).values('proforestform')
            queryset =ProforestForm.objects.filter(id__in = formularios).distinct() #Proforestform asignados

        else:
            queryset =ProforestForm.objects.filter(company_assigned = self.request.user.company) #Proforestform asignados

        if name != None and name != '':
            queryset = queryset.filter( Q(name__icontains=name) | Q(code_form__icontains=name))
        
        if period_id != None and period_id != '':
            period_model = Period.objects.get(id=period_id)
            queryset = queryset.filter(period = period_model)

        return queryset


@permission_classes([CustomDjangoModelPermission])
class ProforestFormCreate(generics.CreateAPIView):
    queryset = ProforestForm.objects.all()
    serializer_class = ProforestFormSerializer

    def perform_create(self, serializer):
        data = self.request.data
        estructura_grupos = {}
        estructura_obligatorios = {}
        estructura_logica_exc = {}
        estructura_logica_grupos = {}
        name_group = {}

        collaborators = data['collaborators']
        array_collaborators = []
        for col in collaborators:
            array_collaborators.append(col['id'])

        bank_questions = data['bank_questions']

        array_questions = []
        for group in bank_questions:
            for index  in group:
                lista = group[index]
                estructura_grupos.setdefault(index, [])

                for elemento in lista:
                    estructura_grupos[index].append(elemento['id'])
                    array_questions.append(elemento['id'])
                    estructura_obligatorios.setdefault(elemento['id'],elemento['required'])

                    if 'logic' in elemento:
                        estructura_logica_exc.setdefault(elemento['id'],elemento['logic'])
                    #creando logica por grupos
                    if 'logic_group' in elemento:
                        estructura_logica_grupos.setdefault(elemento['id'],elemento['logic_group'])

        name_group = data['name_group']

        open_date = dt.datetime.strptime(data['open_date'], '%Y-%m-%d')
        delta = dt.timedelta(days=data['validity_period'])
        expiration_date = open_date+delta
        
        serializer.save(
            created_by = self.request.user,
            collaborators = array_collaborators,
            bank_questions = array_questions,
            group_dict = estructura_grupos,
            required_dict = estructura_obligatorios,
            exclusion_dict = estructura_logica_exc,
            exclusion_logic_group = estructura_logica_grupos,
            name_group = name_group,
            expiration_date = expiration_date.date()
            )
        print("Proforestformcreated questions = ", array_questions)
    
#Api para obtener informacion Basica formulario

@permission_classes([IsAuthenticated])
class ProforestFormView(generics.RetrieveAPIView):
    queryset = ProforestForm.objects.all()
    serializer_class = ProforestFormDetailSerializer


@permission_classes([CustomDjangoModelPermission])
class ProforestFormUpdate(generics.UpdateAPIView):
    queryset = ProforestForm.objects.all()
    serializer_class = ProforestFormUpdateSerializer

    def update(self,request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProforestFormSerializer(instance)

        #Saving dict of versions
        if  instance.data == None:
            instance.data = {'1': serializer.data}
        else:
            instance.data[instance.version] = serializer.data

        instance.version = instance.version+1

        data = self.request.data
        estructura_grupos = {}
        estructura_obligatorios = {}
        estructura_logica_exc = {}
        estructura_logica_grupos = {}


        collaborators = data['collaborators']
        array_collaborators = []
        for col in collaborators:
            array_collaborators.append(col['id'])

        bank_questions = data['bank_questions']

        array_questions = []
        for group in bank_questions:
            
            for index  in group:
                lista = group[index]
                estructura_grupos.setdefault(index, [])
                for elemento in lista:
                    estructura_grupos[index].append(elemento['id'])
                    array_questions.append(elemento['id'])
                    estructura_obligatorios.setdefault(elemento['id'],elemento['required'])
                    if 'logic' in elemento:
                        estructura_logica_exc.setdefault(elemento['id'],elemento['logic'])
                    if 'logic_group' in elemento:
                        estructura_logica_grupos.setdefault(elemento['id'],elemento['logic_group'])
                        
        instance.collaborators.set(array_collaborators)
        instance.required_dict = estructura_obligatorios
        instance.save()

        instance.bank_questions.set(array_questions)
        instance.group_dict = estructura_grupos

        instance.exclusion_dict = estructura_logica_exc
        instance.exclusion_logic_group = estructura_logica_grupos
        instance.name_group = data['name_group']
        
        instance.save()

        return super().update(request, *args, **kwargs)

@permission_classes([CustomDjangoModelPermission])
class ProforestFormDestroy(generics.DestroyAPIView):
    queryset = ProforestForm.objects.all()
    serializer_class = ProforestFormSerializer

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
                        "detail": "ProforestForm cannot be deleted it is asociated to other models.",
                        "attr": "ProforestForm"
                    }
                ]
            },
            403
            )
    

#Api para obtener y repsonder un formulario

@permission_classes([CustomDjangoModelPermission])
class ProforestFormDetail(generics.RetrieveAPIView):
    queryset = ProforestForm.objects.all()
    serializer_class = ProforestFormDetailBankSerializer

    def get_serializer_context(self,  **kwargs):
        context = super(ProforestFormDetail, self).get_serializer_context()
        pagination = self.request.GET.get('pagination')
        page = self.request.GET.get('page')
        context["pagination"] = pagination
        context["page"] = page
        context["path"] = self.request.build_absolute_uri()
        return context

#Api para obtener el codigo tentativo
@permission_classes([IsAuthenticated])
class GetPreviouscode(APIView):
    def get(self, request, format=None):
        """
        Return a tentative code of proforestForm.
        """
        iniciales = "FORM"
        abc = ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
               "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

        if ProforestFormCode.objects.exists():
            pkey = ProforestFormCode.objects.latest('id').pk + 1
        else:
            pkey = 1
        try:
            if pkey <= 99999999:
                code = str(pkey).zfill(8)
                if len(code) < 2:
                    code = code.zfill(7)
                else:
                    code = code.zfill(6)
            else:
                index = pkey // 100000000
                code = str(pkey - (100000000*(pkey//100000000)))
                if len(code) < 2:
                    code = code.zfill(7)
                else:
                    code = code.zfill(6)
                code = abc[index] + code

            proforestcode = str(iniciales+'-'+code)

            return Response({'ProforestFormCode': proforestcode})
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)