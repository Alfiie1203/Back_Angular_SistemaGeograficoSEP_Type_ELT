from apps.utils.permissions import CustomDjangoModelPermission
from apps.company.models.company import Company, CompanyUserFormKey
from apps.company.models.commodity import Commodity
from apps.company.models.actor_type import ActorType
from apps.user.models import User
from apps.user.views.groups import Check_user_in_groups
from apps.supplybase.models.supplybase import SupplyBase

from ..models.formulario import Formulario
from ..models.question import Question, QuestionHistory

from ...proforestform.models.proforestform import ProforestForm, Period

from ..serializers.formulario_serializer import ( FormularioSerializer, FormularioAsignSerializer,
                                                FormularioCreateSerializer, FormularioDetailSerializer,
                                                FormularioSerializerList, FormularioFeedbackDetailSerializer)
from ..serializers.question_serializer import QuestionSerializer, QuestionHistorySerializer
from ..serializers.company_serializer import CompanySerializerList, CompanySerializerListSimple

from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import datetime as dt
import time
from datetime import timedelta, datetime

# =============================================================================
#                           APIREST PROFOREST FORM RESOURCE
# =============================================================================

@permission_classes([CustomDjangoModelPermission])
class FormularioList(generics.ListAPIView):
    serializer_class = FormularioSerializer

    def get_queryset(self):
        status_form = self.request.GET.get('status_form')
        name = self.request.GET.get('name')
        id_company = self.request.GET.get('id_company')
        period_id = self.request.GET.get('period_id')
        date_assing = self.request.GET.get('date_assing')
        date_close = self.request.GET.get('date_close')

        if self.request.user.role.name=='COLABORADOR':
            queryset = Formulario.objects.all()
        else:
            queryset = Formulario.objects.filter(assigned_company=self.request.user.company )

        if (status_form != None and status_form != ''):
            queryset = queryset.filter(status_form=status_form)

        if (name != None and name != ''):
            queryset = queryset.filter(name__icontains=name)

        if (id_company != None and id_company != ''):
            queryset = queryset.filter(allocating_company__id = id_company)

        if period_id != None and period_id != '':
            period_model = Period.objects.get(id=period_id)
            queryset = queryset.filter(period = period_model)

        if (date_assing != None and date_assing != ''):
            date_object = datetime.strptime(date_assing, '%d-%m-%Y')
            queryset = queryset.filter(open_date = date_object)

        if (date_close != None and date_close != ''):
            date_object = datetime.strptime(date_close, '%d-%m-%Y')
            queryset = queryset.filter(expiration_date = date_object)


        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if self.request.user.role.name=='COLABORADOR':
            formularios = Formulario.objects.all()
        else:
            formularios = Formulario.objects.filter(assigned_company=self.request.user.company )
        empresas = formularios.values('allocating_company')
        companies = Company.objects.filter(id__in = empresas).distinct()

        array = []
        for company in companies:
            dict = {}
            dict['name_company'] = company.name
            dict['id_company'] = company.id
            
            array.append(dict)
        response.data['list_companies_asignadoras'] = array

        return response

from django.http import JsonResponse

@permission_classes([IsAuthenticated])
class FormularioAsign(APIView):

    queryset = Formulario.objects.all()
    serializer_class = FormularioAsignSerializer

    def post(self,request):
        data = dict(request.data)

        if self.request.user.role.name=='COLABORADOR':
            proforestform = ProforestForm.objects.get(pk=data['proforestform'])
            assigned_companies = data['assigned_companies']
            today = dt.datetime.now().date()
            
            for company in assigned_companies:
                response_dict={}
                partner_company = Company.objects.get(id=company['id'])
                proforestform.company_assigned.add(partner_company)
                proforestform.save()    # Hasta acá garantizo que ya es partner la empresa del formulario
                #Ahora si lo mando como base es para que se dispare de una los FORMULARIOS

                if company['supply_base']:
                    data['allocating_company'] = partner_company.id
                    data['send_to_company_suply_base'] = company['supply_base']
                    data['created_by'] = self.request.user.id
                    data['code_form'] = proforestform.code_form
                    data['name'] = proforestform.name

                    #si hoy es menor o igual que la fecha de apertura  se crea el primer formulario con las mismas fechas de una vez

                    if today <= proforestform.open_date:
                        data['open_date'] = proforestform.open_date
                        data['expiration_date'] = proforestform.open_date + timedelta(proforestform.validity_period)
                        data['validity_period'] = proforestform.validity_period
                        data['period'] = proforestform.period.id
                        data['status_form']='ACTIVE' #PARA MANIPULAR SI NO VA ESTE ESTADO POR DEFAULT

                    else:
                        data['open_date'] = today
                        data['expiration_date'] = today + timedelta(proforestform.validity_period)
                        data['validity_period'] = proforestform.validity_period
                        data['period'] = proforestform.period.id
                        data['status_form']='ACTIVE'


                    listado = SupplyBase.objects.filter(company = partner_company )
                    for item in listado:
                        assigned_company = item.supplier_company
                        name_assigned_company = assigned_company.name
                        data['assigned_company'] = assigned_company.id #id de la assigned company
                        serializer = FormularioAsignSerializer(data=data)
                        if serializer.is_valid():
                            if Formulario.objects.filter(proforestform__id= proforestform.id, allocating_company = partner_company, assigned_company = assigned_company).exists():
                                formulario = Formulario.objects.filter(proforestform= proforestform.id, allocating_company = partner_company, assigned_company = assigned_company)[0]
                                formulario.send_to_company_suply_base = True
                                formulario.save()
                                
                            else:
                                formulario = serializer.save()
                                formulario.bank_questions.set(proforestform.bank_questions.all())
                                formulario.save()
                                formulario.assigned_form_email()
                                time.sleep(2) #Prevent exced maximun email sended in a time
                            
                            response_dict[name_assigned_company] = "Succesfull form created"
                            
                        else:
                            response_dict[name_assigned_company] = "Error not asigned the form"
                else:
                    response_dict[partner_company.name] = "Succesfull proforestform assigned to partner"
            
        else: #La asignacion es directa
            allocating_company = request.user.company
            proforestform = ProforestForm.objects.get(pk=data['proforestform'])
            assigned_companies = data['assigned_companies']
            data['created_by'] = self.request.user.id
            data['code_form'] = proforestform.code_form
            data['name'] = proforestform.name
            response_dict={}

            for company in assigned_companies:

                assigned_company = Company.objects.get(id = company['id'] )
                today = dt.datetime.now().date()
                data['allocating_company'] = allocating_company.id
                #si hoy es menor o igual que la fecha de apertura  se crea el primer formulario con las mismas fechas de una vez
                if today <= proforestform.open_date:
                    data['open_date'] = proforestform.open_date
                    data['expiration_date'] = proforestform.open_date + timedelta(proforestform.validity_period)
                    data['validity_period'] = proforestform.validity_period
                    data['period'] = proforestform.period.id
                    data['status_form']='ACTIVE' #PARA MANIPULAR SI NO VA ESTE ESTADO POR DEFAULT

                else:
                    data['open_date'] = today
                    data['expiration_date'] = today + timedelta(proforestform.validity_period)
                    data['validity_period'] = proforestform.validity_period
                    data['period'] = proforestform.period.id
                    data['status_form']='ACTIVE' #PARA MANIPULAR SI NO VA ESTE ESTADO POR DEFAULT


                data['assigned_company'] = company['id']
                serializer = FormularioAsignSerializer(data=data)
                if serializer.is_valid():

            
                    if Formulario.objects.filter(proforestform__id= proforestform.id, allocating_company=self.request.user.company, assigned_company = assigned_company).exists():
                        formulario = Formulario.objects.filter(proforestform__id= proforestform.id, allocating_company=self.request.user.company, assigned_company = assigned_company)[0]
                        formulario.send_to_company_suply_base = company['supply_base']
                        formulario.save()
                        print(">>>>No se envia correo, Actualizado formulario ya creado no.", formulario.id)

                    else:
                        formulario = serializer.save()
                        formulario.bank_questions.set(proforestform.bank_questions.all())
                        formulario.save()
                        print(">>>>Se envia correo Creando formulario Nuevo No.", formulario.id)
                        time.sleep(3) #Prevent exced maximun email sended in a time
                        formulario.assigned_form_email()

                    response_dict[assigned_company.name] = "Succesfull form assigned"
                    

                else:
                    response_dict[assigned_company.name] = "Error not asigned the form"
            
            supplier_companies = SupplyBase.objects.filter(company = self.request.user.company).values('supplier_company')
            companies = Company.objects.filter(id__in = supplier_companies, has_responsable=True).distinct()
            id_companylist = [company['id'] for company in assigned_companies]

            for company in companies:
                company_dict = {}
                company_dict['id'] = company.id
                company_dict['name'] = company.name
                if Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).exists():
                    lastform_created = Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).last()
                    if company.id in id_companylist:
                        lastform_created.active_next_period = True #Es decir sigue asignado
                        lastform_created.save()
                    else:
                        lastform_created.active_next_period = False #Es decir queda desasignado para el siguiente periodo
                        lastform_created.save()

                else:
                    pass
                    #Es decir no ha sido asignado de mi company para ese supplier
            #end actualizacion
            
                    
        return JsonResponse({"response": response_dict }, status=201)

#Assign to a new company not registered

@permission_classes([IsAuthenticated])
class FormularioEmailAsignCompany(APIView):

    queryset = Formulario.objects.all()
    serializer_class = FormularioAsignSerializer

    def post(self,request):

        if self.request.user.role.name=='COLABORADOR':
            return Response(
                {
                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "allocating_company",
                            "detail": "Asigned Companies by colaborator not permited allocating company cant be null",
                            "attr": "Formulario"
                        }
                    ]
                },
                403
            )
        else:
            allocating_company = request.user.company
        data = dict(request.data)
        proforestform = ProforestForm.objects.get(pk=data['proforestform'])
        assigned_companies = data['assigned_companies']
        data['created_by'] = self.request.user.id
        data['code_form'] = proforestform.code_form
        data['name'] = proforestform.name
    
        if assigned_companies == []:
            return Response(
                {
                    "type": "validation_error",
                    "errors": [
                        {
                            "code": "assigned_companies",
                            "detail": "Asigned Companies cannot be empty.",
                            "attr": "Formulario"
                        }
                    ]
                },
                403
            )
        
        response_dict={}

        for assign_data in assigned_companies:
            email = assign_data["email"]    #to generate Slug Token
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        "type": "validation_error",
                        "errors": [
                            {
                                "code": "assigned_user",
                                "detail": "The user already exists in the database, belongs to another company ",
                                "attr": "User"
                            }
                        ]
                    },
                    403
                )                                                                                 
            company = Company.objects.get(id = assign_data["id_company"])
            today = dt.datetime.now().date()
            data['allocating_company'] = allocating_company.id # Quien asigno el formulario
            data['assigned_company'] = assign_data['id_company']
            data['send_to_company_suply_base'] = assign_data['supply_base']
            #si hoy es menor o igual que la fecha de apertura  se crea el primer formulario con las mismas fechas de una vez
            if today <= proforestform.open_date:
                data['open_date'] = proforestform.open_date
                data['expiration_date'] = proforestform.open_date + timedelta(proforestform.validity_period)
                data['validity_period'] = proforestform.validity_period
                data['period'] = proforestform.period.id
            else:
                data['open_date'] = today
                data['expiration_date'] = today + timedelta(proforestform.validity_period)
                data['validity_period'] = proforestform.validity_period
                data['period'] = proforestform.period.id

            data['status_form']='ACTIVE'
            serializer = FormularioAsignSerializer(data=data)

            if serializer.is_valid():

                if Formulario.objects.filter(proforestform__id= proforestform.id, assigned_company = assign_data['id_company']).exists():
                    formulario = Formulario.objects.get(proforestform__id= proforestform.id, assigned_company = assign_data['id_company'])
                    formulario.send_to_company_suply_base = assign_data['supply_base']
                    formulario.save()
                    
                else:
                    formulario = serializer.save()
                    formulario.bank_questions.set(proforestform.bank_questions.all())
                    formulario.save()

                
                response_dict[company.name] = "Succesfull form assigned"
                
            else:
                response_dict[company.name] = "Error not asigned the form"

            companyuserformkey = CompanyUserFormKey.objects.create(
                company = company,
                email = email
            )
            formulario.assigned_new_user_form_email(email, companyuserformkey.slug)
        return JsonResponse({"response": response_dict }, status=201)



#Api para obtener y repsonder un formulario

@permission_classes([IsAuthenticated])
class FormularioDetail(generics.RetrieveAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioDetailSerializer

    def get_serializer_context(self,  **kwargs):
        context = super(FormularioDetail, self).get_serializer_context()
        pagination = self.request.GET.get('pagination')
        page = self.request.GET.get('page')
        language_code = self.request.headers.get('Content-Language')    

        context["language_code"] = language_code
        context["pagination"] = pagination
        context["page"] = page
        context["path"] = self.request.build_absolute_uri()
        return context

#Api for Fill or update answers

@permission_classes([IsAuthenticated])
class AnswerQuestion(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_update(self, serializer):
        data = self.request.data
        user = self.request.user
        
        if 'reviewer_observations' in data:
            question = serializer.save(
                reviewed_by = user,
                
                )
            QuestionHistory.objects.create(
                validation = question.validation,
                question = question,
                reviewed_by = question.reviewed_by,
                reviewer_observations = question.reviewer_observations,
                answered_by = question.answered_by,
                answer = question.answer
            )
        else:
            question = serializer.save(
            answered_by = user,
            )

#Ojo Vamos a modificar la asignacion
@permission_classes([IsAuthenticated])
class ListCompanies(generics.ListAPIView):
    def get(self, request, format=None):
        """
        Return two dicts one available Companies the other selected by some Form
        """
        id_proforestform = self.request.GET.get('proforestform')
        proforestform = ProforestForm.objects.get(id = id_proforestform)
        if self.request.user.role.name=='COLABORADOR':
            print("es un COLABORADOR admin o super admin cargamos las empresas con SUPERUSUARIO ASIGNADO")
            companies = Company.objects.filter(has_superuser=True)

            #Listado desplegable superior
            list_companies = []
            for company in companies:
                company_dict = {}
                if company in proforestform.company_assigned.all():
                    company_dict['id'] = company.id
                    company_dict['name'] = company.name
                    company_dict['supply_base'] = True 
                    
                else:
                    company_dict['id'] = company.id
                    company_dict['name'] = company.name
                    company_dict['supply_base'] = False 
                list_companies.append(company_dict)


            list_selected_companies = []
            for company in companies:
                company_dict = {}
                if company in proforestform.company_assigned.all():
                    company_dict['id'] = company.id
                    company_dict['name'] = company.name
                    company_dict['supply_base'] = True #SI lo habian metido en la lista
                    list_selected_companies.append(company_dict)
                else:
                    pass # "NO estaba asignado"

            return Response({'list_companies': list_companies, 'list_selected_companies': list_selected_companies})
        else:
            print("GENERANDO TABLAS PARA  un SUPERUSER")
            supplier_companies = SupplyBase.objects.filter(company = self.request.user.company).values('supplier_company')
            companies = Company.objects.filter(id__in = supplier_companies, has_responsable=True).distinct()
            #Listado desplegable superior CON EMPRESAS QUE SON  SUPLIERS DEL SUPERUSER Y QUE TIENEN responsable 
            list_companies = []

            for company in companies:
                company_dict = {}
                company_dict['id'] = company.id
                company_dict['name'] = company.name
                if Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).exists():
                    lastform_created = Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).last()
                    company_dict['supply_base'] = lastform_created.active_next_period #Es decir ya fue asignado el pasado pero no el siguiente

                else:
                   company_dict['supply_base'] = False #Es decir no ha sido asignado de mi company para es supplier

                list_companies.append(company_dict)

            list_selected_companies = []
            for company in companies:
                company_dict = {}
                company_dict['id'] = company.id
                company_dict['name'] = company.name
                if Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).exists():
                    lastform_created = Formulario.objects.filter(proforestform=proforestform, allocating_company=self.request.user.company, assigned_company=company).last()
                    if lastform_created.active_next_period:
                        company_dict['supply_base'] = lastform_created.active_next_period #Es decir ya fue asignado el pasado pero no el siguiente
                        list_selected_companies.append(company_dict)

                else:
                    company_dict['supply_base'] = False #Es decir no ha sido asignado de mi company para es supplier


            return Response({'list_companies': list_companies, 'list_selected_companies': list_selected_companies})


        


@permission_classes([IsAuthenticated])
class SubmitFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, serializer):
        serializer.save(
            answered_by = self.request.user,
        )
        dictionary = self.request.data
        bank_questions_answers = dictionary["respuesta"]
        
        for group in bank_questions_answers:
            for index  in group:
                lista = group[index]
                for elemento in lista:

                    try:
                        question_id = elemento['id']
                        content_text = elemento['response']
                        question = Question.objects.get(id = question_id)

                        if question.question_data['type'] == 'open_answer':
                            question.answer = content_text

                        elif question.question_data['type'] == 'select_one':
                            choices = question.question_data['choices']
                            for index in choices:
                                data_choices = choices[index]
                                if content_text in data_choices.values():
                                    question.answer = {index:data_choices}

                        elif question.question_data['type'] == 'select_multiple':
                            rta_final = []
                            for respuesta in content_text:
                                choices = question.question_data['choices']
                                estructura_respuesta = {}
                                for index in choices:
                                    data_choices = choices[index]
                                    if respuesta in data_choices.values():
                                        estructura_respuesta[index]=data_choices
                                        rta_final.append(estructura_respuesta)
                                question.answer = rta_final

                        elif question.question_data['type'] == 'matrix_select_multiple':
                            rta_final = []
                            rows = question.question_data['rows']
                            columns = question.question_data['columns']
                            array = []
                            for pregunta in content_text:
                                for posibles in rows:
                                    if pregunta in rows[posibles].values():
                                        preg = (rows[posibles])
                                        rta_bruto = content_text[pregunta]
                                        for rta_one in rta_bruto:
                                            for col in columns:
                                                if rta_one in columns[col].values():
                                                    lista  = [preg,columns[col]]
                                                    array.append(lista)
                            question.answer = array

                        elif question.question_data['type'] == 'matrix_select_one':

                            if question.question_data['appearance'] == 'dropdown_list':
                                columns_options = question.question_data['column_choices']
                                array = []

                                for respuesta_location in content_text:
                                    location = respuesta_location.split('_')
                                    respuesta = content_text[respuesta_location]
                                    columna = location[1]
                                    for opciones_columna in columns_options[columna]:
                                        opcion =   columns_options[columna][opciones_columna]
                                        if respuesta in opcion.values():
                                            location.append(opcion)
                                            array.append(location)
                                question.answer = array
                                
                            elif question.question_data['appearance'] == 'radio':

                                rows_question = question.question_data['rows']
                                columns_answer = question.question_data['columns']
                                array=[]

                                for pregunta in content_text:
                                    for pregunta_db in rows_question:
                                        if pregunta in rows_question[pregunta_db].values():
                                            pregunta_original = rows_question[pregunta_db]
                                            respuesta = content_text[pregunta]
                                            for respuesta_db in columns_answer:
                                                if respuesta in columns_answer[respuesta_db].values():
                                                    respuesta_original = columns_answer[respuesta_db]
                                                    lista = [pregunta_original, respuesta_original]
                                                    array.append(lista)
                                question.answer = array

                            else:
                                rta_final = []
                                rows = question.question_data['rows']
                                columns = question.question_data['columns']
                                array = []
                                for pregunta in content_text:
                                    for posibles in rows:
                                        if pregunta in rows[posibles].values():
                                            preg = (rows[posibles])
                                            rta_bruto = content_text[pregunta]
                                            for rta_one in rta_bruto:
                                                for col in columns:
                                                    if rta_one in columns[col].values():
                                                        lista  = [preg,columns[col]]
                                                        array.append(lista)
                                question.answer = array


                        elif question.question_data['type'] == 'file_upload':
                            question.answer = content_text

                        question.answered_by = self.request.user
                        question.save()
                        
                    except Exception as e:
                        pass

        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})

@permission_classes([IsAuthenticated])
class AsignedFormulariosProforestform(generics.ListAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializerList

    def get_queryset(self):
        name = self.request.GET.get('name')
        commodity_id = self.request.GET.get('commodity')
        actortype_id = self.request.GET.get('actor_type')
        
        proforestform_id = self.request.resolver_match.kwargs['pk']
        formularios = Formulario.objects.filter(proforestform__id=proforestform_id, revisor = self.request.user)

        if (name != None and name != ''):
            formularios = formularios.filter(assigned_company__name__icontains=name)

        if commodity_id != None and commodity_id != '':
            commodity_model = Commodity.objects.get(id=commodity_id)
            formularios = formularios.filter(assigned_company__commodity=commodity_model)

        if actortype_id != None and actortype_id != '':
            actortype_model = ActorType.objects.get(id=actortype_id)
            formularios = formularios.filter(assigned_company__actor_type=actortype_model)
        

        return formularios
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        proforestform_id = self.request.resolver_match.kwargs['pk']
        formulario = Formulario.objects.filter(proforestform__id=proforestform_id)[0]
        response.data['formulario_name'] = formulario.name

        return response


#Posible delete
#Api para obtener informacion Basica formulario

@permission_classes([CustomDjangoModelPermission])
class FormularioView(generics.RetrieveAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializer
    
#===========================end Posible delete

@permission_classes([IsAuthenticated])
class CheckVersionFile(APIView):
    '''Return from a list the most recent register'''
    def post(self, request):
        dictionary = self.request.data
        drive_items = dictionary['value']
        name_file = dictionary['name_file']
        temp_data = []
        for e in drive_items:
            if (name_file in e['name']):
                temp_data.append(e)
        most_recent = max(temp_data, key = lambda item: item['createdDateTime'])
        return Response({'data': most_recent})


@permission_classes([IsAuthenticated])
class ListNoResponsableCompanies(generics.ListAPIView):
    def get(self, request, format=None):
        """
        Return two dicts one available Companies the other selected by some Form
        """
        if self.request.user.role.name=='COLABORADOR':
            companies = Company.objects.filter(has_responsable=False)
        else:
            supplier_companies = SupplyBase.objects.filter(company = self.request.user.company).values('supplier_company')
            companies = Company.objects.filter(id__in = supplier_companies, has_responsable=False).distinct()

        list_companies = []
        
        for company in companies:
            company_dict = {}
            company_dict['id'] = company.id
            company_dict['name'] = company.name
            list_companies.append(company_dict)


        return Response({'list_companies': list_companies})


@permission_classes([IsAuthenticated])
class HistoryQuestion(generics.ListAPIView):
    serializer_class = QuestionHistorySerializer
    queryset = QuestionHistory.objects.all()

    def get_queryset(self):
        question_id = self.request.resolver_match.kwargs['pk']
        historial = QuestionHistory.objects.filter(question__id=question_id)
        return historial

#Submitt Validate of form

@permission_classes([IsAuthenticated])
class SubmitValidateFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, request):
        formulario = self.get_object()
        formulario.revision_status='VALIDATE'
        formulario.save()
        try:
            formulario.validate_form_email()
            time.sleep(3)
            formulario.validate_info_assigned_company()
        except:
            print("Cant send emails")
        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})

@permission_classes([IsAuthenticated])
class SubmitPartialValidateFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, request):
        obj = self.get_object()
        obj.revision_status='INVALIDATINGPROCESS'
        obj.save()
        try:
            obj.validate_form_email()
            time.sleep(3)
            obj.validate_info_assigned_company()
        except:
            print("cant send emails")
        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})


#Submitt VERIFICATION of form

@permission_classes([IsAuthenticated])
class SubmitVerificateFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, request):
        formulario = self.get_object()
        formulario.revision_status='VERIFIED'
        formulario.save()
        try:
            formulario.verificate_form_email()
            time.sleep(3)
            formulario.verificate_info_assigned_company()
        except:
            print("cant send emails")

        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})

@permission_classes([IsAuthenticated])
class SubmitPartialVerificateFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, request):
        obj = self.get_object()
        obj.revision_status='INVERIFYPROCESS'
        obj.save()
        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})

@permission_classes([CustomDjangoModelPermission])
class ListFormulariosAssignedByMe(generics.ListAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializerList

    def get_queryset(self,):
        proforestform_id = self.request.GET.get('proforestform_id')
        period_id = self.request.GET.get('period_id')
        companyassigned_id = self.request.GET.get('companyassigned_id')

        if self.request.user.role.name=='COLABORADOR':
            queryset = Formulario.objects.all()
        else:
            queryset = Formulario.objects.filter(allocating_company=self.request.user.company)

        if proforestform_id:
            queryset = queryset.filter(proforestform__id = proforestform_id)
        if period_id:
            queryset = queryset.filter(period__id = period_id)
        if companyassigned_id:
            queryset = queryset.filter(assigned_company__id = companyassigned_id)

        return queryset
    
@permission_classes([CustomDjangoModelPermission])
class ListAssignedForms(generics.ListAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializerList

    def get_queryset(self,):
        proforestform_name = self.request.GET.get('proforestform_name')
        period_id = self.request.GET.get('period_id')
        year = self.request.GET.get('year')
        company_assigned_name = self.request.GET.get('company_assigned_name')
        company_allocator_name = self.request.GET.get('company_allocator_name')

        date_assing = self.request.GET.get('date_assing')
        date_close = self.request.GET.get('date_close')
        status_form = self.request.GET.get('status_form')
        code_form = self.request.GET.get('code_form')

        if Check_user_in_groups(self.request.user, ['SUPERADMINISTRADOR']):
            queryset = Formulario.objects.all()
        elif Check_user_in_groups(self.request.user, ['ADMINISTRADOR']):
            proforest_forms = ProforestForm.objects.filter(collaborators = self.request.user).values('id')
            queryset = Formulario.objects.filter(proforestform__in = proforest_forms)
        elif Check_user_in_groups(self.request.user, ['SUPERUSUARIO']):
            queryset = Formulario.objects.filter(allocating_company=self.request.user.company)
        elif Check_user_in_groups(self.request.user, ['USUARIO']):
            queryset = Formulario.objects.filter(assigned_company=self.request.user.company)
        else:
            queryset = Formulario.objects.none()

        if proforestform_name:
            queryset = queryset.filter(name__icontains = proforestform_name)

        if (status_form != None and status_form != ''):
            queryset = queryset.filter(status_form=status_form)

        if period_id:
            queryset = queryset.filter(period__id = period_id)
        if year:
            queryset = queryset.filter(created_at__year = year )
        if company_assigned_name:
            queryset = queryset.filter(assigned_company__name__icontains = company_assigned_name)
        if company_allocator_name:
            queryset = queryset.filter(allocating_company__name__icontains = company_allocator_name)

        if (date_assing != None and date_assing != ''):
            date_object = datetime.strptime(date_assing, '%d-%m-%Y')
            queryset = queryset.filter(open_date = date_object)

        if (date_close != None and date_close != ''):
            date_object = datetime.strptime(date_close, '%d-%m-%Y')
            queryset = queryset.filter(expiration_date = date_object)

        if (code_form != None and code_form != ''):
            queryset = queryset.filter(period_code__icontains=str(code_form))

        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        proforestform_name = self.request.GET.get('proforestform_name')
        period_id = self.request.GET.get('period_id')
        year = self.request.GET.get('year')
        company_assigned_name = self.request.GET.get('company_assigned_name')
        company_allocator_name = self.request.GET.get('company_allocator_name')

        date_assing = self.request.GET.get('date_assing')
        date_close = self.request.GET.get('date_close')
        status_form = self.request.GET.get('status_form')

        if Check_user_in_groups(self.request.user, ['SUPERADMINISTRADOR']):
            queryset = Formulario.objects.all()
        elif Check_user_in_groups(self.request.user, ['ADMINISTRADOR']):
            proforest_forms = ProforestForm.objects.filter(collaborators = self.request.user).values('id')
            queryset = Formulario.objects.filter(proforestform__in = proforest_forms)
        elif Check_user_in_groups(self.request.user, ['SUPERUSUARIO']):
            queryset = Formulario.objects.filter(allocating_company=self.request.user.company)
        elif Check_user_in_groups(self.request.user, ['USUARIO']):
            queryset = Formulario.objects.filter(assigned_company=self.request.user.company)
        else:
            queryset = Formulario.objects.none()
        if proforestform_name:
            queryset = queryset.filter(name__icontains = proforestform_name)

        if (status_form != None and status_form != ''):
            queryset = queryset.filter(status_form=status_form)

        if period_id:
            queryset = queryset.filter(period__id = period_id)
        if year:
            queryset = queryset.filter(created_at__year = year )
        if company_assigned_name:
            queryset = queryset.filter(assigned_company__name__icontains = company_assigned_name)
        if company_allocator_name:
            queryset = queryset.filter(allocating_company__name__icontains = company_allocator_name)

        if (date_assing != None and date_assing != ''):
            date_object = datetime.strptime(date_assing, '%d-%m-%Y')
            queryset = queryset.filter(open_date = date_object)

        if (date_close != None and date_close != ''):
            date_object = datetime.strptime(date_close, '%d-%m-%Y')
            queryset = queryset.filter(expiration_date = date_object)
            
        codes = list(queryset.values('period_code'))
        unique_codes = {d['period_code'] for d in codes}

        array = []
        for code in unique_codes:
            dict = {}
            dict['code'] = code
            array.append(dict)
        response.data['list_codes_form'] = array

        return response
    

@permission_classes([IsAuthenticated])
class FinishFormulario(generics.UpdateAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioCreateSerializer

    def perform_update(self, serializer):
        serializer.save(
            answered_by = self.request.user,
            # status_form = 'FINISHED',             #####   ojo aca toca dejarlo normal PILAS <<<<<<<<<<
        )
        dictionary = self.request.data
        bank_questions_answers = dictionary["respuesta"]
        for group in bank_questions_answers:
            for index  in group:
                lista = group[index]
                for elemento in lista:
                    try:
                        question_id = elemento['id']
                        content_text = elemento['response']
                        question = Question.objects.get(id = question_id)
                        
                        if question.question_data['type'] == 'open_answer':
                            question.answer = content_text

                        elif question.question_data['type'] == 'select_one':
                            choices = question.question_data['choices']
                            for index in choices:
                                data_choices = choices[index]
                                if content_text in data_choices.values():
                                    question.answer = {index:data_choices}

                        elif question.question_data['type'] == 'select_multiple':
                            rta_final = []
                            for respuesta in content_text:
                                choices = question.question_data['choices']
                                estructura_respuesta = {}
                                for index in choices:
                                    data_choices = choices[index]
                                    if respuesta in data_choices.values():
                                        estructura_respuesta[index]=data_choices
                                        rta_final.append(estructura_respuesta)
                                question.answer = rta_final
                            



                        elif question.question_data['type'] == 'matrix_select_multiple':
                            rta_final = []
                            rows = question.question_data['rows']
                            columns = question.question_data['columns']
                            array = []
                            for pregunta in content_text:
                                for posibles in rows:
                                    if pregunta in rows[posibles].values():
                                        preg = (rows[posibles])
                                        rta_bruto = content_text[pregunta]
                                        for rta_one in rta_bruto:
                                            for col in columns:
                                                if rta_one in columns[col].values():
                                                    lista  = [preg,columns[col]]
                                                    array.append(lista)
                            question.answer = array

                        elif question.question_data['type'] == 'matrix_select_one':

                            if question.question_data['appearance'] == 'dropdown_list':
                                columns_options = question.question_data['column_choices']
                                array = []

                                for respuesta_location in content_text:
                                    location = respuesta_location.split('_')
                                    respuesta = content_text[respuesta_location]
                                    columna = location[1]
                                    for opciones_columna in columns_options[columna]:
                                        opcion =   columns_options[columna][opciones_columna]
                                        if respuesta in opcion.values():
                                            location.append(opcion)
                                            array.append(location)
                                question.answer = array
                                
                            elif question.question_data['appearance'] == 'radio':

                                rows_question = question.question_data['rows']
                                columns_answer = question.question_data['columns']
                                array=[]

                                for pregunta in content_text:
                                    for pregunta_db in rows_question:
                                        if pregunta in rows_question[pregunta_db].values():
                                            pregunta_original = rows_question[pregunta_db]
                                            respuesta = content_text[pregunta]
                                            for respuesta_db in columns_answer:
                                                if respuesta in columns_answer[respuesta_db].values():
                                                    respuesta_original = columns_answer[respuesta_db]
                                                    lista = [pregunta_original, respuesta_original]
                                                    array.append(lista)
                                question.answer = array

                            else:
                                rta_final = []
                                rows = question.question_data['rows']
                                columns = question.question_data['columns']
                                array = []
                                for pregunta in content_text:
                                    for posibles in rows:
                                        if pregunta in rows[posibles].values():
                                            preg = (rows[posibles])
                                            rta_bruto = content_text[pregunta]
                                            for rta_one in rta_bruto:
                                                for col in columns:
                                                    if rta_one in columns[col].values():
                                                        lista  = [preg,columns[col]]
                                                        array.append(lista)
                                question.answer = array


                        elif question.question_data['type'] == 'file_upload':
                            question.answer = content_text

                        question.answered_by = self.request.user
                        question.save()
                        
                    except Exception as e:
                        pass

        #update blank questions if exclusion
        for group in bank_questions_answers:
            for index  in group:
                lista = group[index]
                for elemento in lista:
                    #funcion que setea respuestas por logica de exclusion a Nulas
                    try:
                        logic_group = elemento['logic_group']
                        for a in logic_group:
                            value = logic_group[a]
                            answer = Question.objects.get(id=a).answer
                            answer_value = list(answer.values())[0] # Just capture the answer value
                            value_dict = value[0]['option'][0]['id']
                            # print("VALUE_DICT ", value_dict)
                            # print("ANSWER_VALUE ", answer_value)
                            condition = value[0]['condition']['id']
                            expresion = 'answer_value ' + condition + ' value_dict'
                            if eval(expresion):
                                group_exclude = value[0]['source_groups']
                                formulario = Question.objects.get(id=a).formulario
                                preguntas_descartar = Question.objects.get(id=a).formulario.proforestform.group_dict[str(group_exclude)]
                                for pregunta in preguntas_descartar:
                                    pregunta_seteada = Question.objects.get(formulario= formulario, question_bank__id = pregunta)
                                    pregunta_seteada.answered_by = None
                                    pregunta_seteada.answer = None
                                    pregunta_seteada.save()
                            else:
                                pass #  NO SE CUMPLE LA CONDICION DE EXCLUSION
                    except Exception as e:
                        print(e)
                #end update exclusion

        return Response({'info': 'formulario updated', 'id_formulario': self.get_object()})



#Api para obtener las rtas y sus feedbacks de los validadores o verificadores

@permission_classes([IsAuthenticated])
class FormularioFeedback(generics.RetrieveAPIView):
    queryset = Formulario.objects.all()
    serializer_class = FormularioFeedbackDetailSerializer

    def get_serializer_context(self,  **kwargs):
        context = super(FormularioFeedback, self).get_serializer_context()
        pagination = self.request.GET.get('pagination')
        page = self.request.GET.get('page')
        language_code = self.request.headers.get('Content-Language')    

        context["language_code"] = language_code
        context["pagination"] = pagination
        context["page"] = page
        context["path"] = self.request.build_absolute_uri()
        return context