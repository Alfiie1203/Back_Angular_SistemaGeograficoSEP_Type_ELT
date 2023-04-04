from rest_framework import serializers
from ..models.formulario import Formulario
from apps.company.models.company import QuestionDriveSubCategoryFolder
from apps.formulario.models.question import Question
from apps.proforestform.serializers.period_serializer import PeriodSerializer
from apps.company.serializers.company_serializer import CompanySerializerDetail
from django.core.paginator import Paginator

from apps.onedrive.models import Token
import requests
import json

from config.settings import URL_GETFILE


class FormularioSerializer(serializers.ModelSerializer):

    allocating_company = serializers.ReadOnlyField(source='allocating_company.name')
    assigned_company = serializers.ReadOnlyField(source='assigned_company.name')
    period = PeriodSerializer()
    percentage_completion =serializers.SerializerMethodField('get_percentage')
    class Meta:
        model = Formulario
        fields = [ 'id', 'proforestform', 'code_form', 'name', 'created_by',
        'open_date', 'expiration_date', 'validity_period',
        'allocating_company', 'revision_status',  'assigned_company',
        'revisor', 
        'send_to_company_suply_base', 'period', 'bank_questions',
        'status_form',
        'percentage_completion' 
        ]

    def get_percentage(self, obj):
        return obj.percentage_of_completion()

class FormularioAsignSerializer(serializers.ModelSerializer):

    # assigned_companies = serializers.ListField()

    class Meta:
        model = Formulario
        fields = [ 'id', 'proforestform', 'name',
        'open_date', 'expiration_date', 'validity_period',
        'allocating_company', 'revision_status', 'status_form', 
        'revisor', 
        'send_to_company_suply_base', 'period',
        'assigned_company',
        'code_form', 'created_by',
        ]


class FormularioCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Formulario
        fields = [
            'id',
            'id', 'code_form', 'name','created_by', 
            'open_date', 'expiration_date', 'validity_period', 'period',
        ]

class FormularioDetailSerializer(serializers.ModelSerializer):

    # percentage_completion = serializers.SerializerMethodField('get_percentage') #suspendido para que la lista pueda traer el porentaje bien
    question_package = serializers.SerializerMethodField('get_question_list')
    name_group = serializers.ReadOnlyField(source='proforestform.name_group')
    # next = serializers.SerializerMethodField('get_next_page')
    # back = serializers.SerializerMethodField('get_back_page')


    class Meta:
        model = Formulario
        fields = [
            'id',
            # 'next',
            # 'back',
            'id', 'code_form', 'name','created_by', 
            'open_date', 'expiration_date', 'validity_period', 'period',
            'question_package',
            # 'percentage_completion',
            'name_group',
            'revision_status',
            'status_form'
        ]
    def get_percentage(self, obj):
        return obj.percentage_of_completion()
        
    def get_question_list(self,obj):
        group_dict = obj.proforestform.group_dict
        required_dict = obj.proforestform.required_dict
        language_code = self.context["language_code"]
        exclusion_dict = obj.proforestform.exclusion_dict
        exclusion_logic_group = obj.proforestform.exclusion_logic_group

        question_data ={}
        banderas_file_relationship=[]

        for group in group_dict:
            question_data.setdefault(group,[])
            for question_id in group_dict[group]:
                lista = list(Question.objects.filter(formulario=obj, question_bank__id=question_id).values("id", "question_data", "status", "validation", "answer", "answered_by", "group", "reviewed_by", "reviewer_observations" ))
                if Question.objects.filter(formulario=obj, question_bank__id=question_id).exists():
                    try:
                        lista[0]['required'] = required_dict[str(question_id)]
                    except:
                        print("question not required")
                    new_url_file = None
                    if lista[0]['question_data']['type']=="file_upload":
                        question_analizada = Question.objects.get(id=int(lista[0]['id']))
                        lista[0]['id_drivefolder'] = QuestionDriveSubCategoryFolder.objects.get(
                            category = question_analizada.question_bank.category,
                            subcategory = question_analizada.question_bank.subcategory,
                            company = question_analizada.formulario.assigned_company
                            ).drive_folder_subcategory_id
                        if question_analizada.answer:
                            id_file = question_analizada.answer['id']
                            token = Token.objects.latest()
                            headers = {
                                'Content-Type': 'application/json',
                                'Authorization': token.access_token
                                }
                            url_file = URL_GETFILE + id_file
                            responsems = requests.get(url_file, headers=headers)
                            result_ms_url = responsems.json()
                            new_url_file = result_ms_url['@microsoft.graph.downloadUrl']
                    try:    
                        response = Question.objects.get(formulario=obj, question_bank__id=question_id).get_response(language=language_code)
                        if response == None:
                            response = Question.objects.filter(answered_by__company=obj.assigned_company, question_bank__id=question_id).order_by('-last_modified')[0].get_response(language=language_code)
                    except:
                        response = None
                    #exclusion por pregunta
                    if str(question_id) in exclusion_dict:
                        array_logica = exclusion_dict[str(question_id)]
                        for element in array_logica:
                            for i, id_dict in enumerate(element['ids']):
                                id_form_question = Question.objects.get(formulario=obj, question_bank__id=id_dict['id']).id
                                id_dict['id'] = id_form_question
                                banderas_file_relationship.append(id_form_question)
                        lista[0]['logic'] = array_logica
                    else:
                        form_question = Question.objects.get(formulario=obj, question_bank__id=question_id)
                        if (form_question.id in banderas_file_relationship) and (form_question.question_data['type'] == 'file_upload'):
                            # print("coloca antecedente") #El antecedente es para cuando las preguntas se conectan con un archivo para solo evaluar uno
                            lista[0]['file_exclude'] = True

                    #exclusionde grupo
                    if str(question_id) in exclusion_logic_group:
                        id_formulario_question = Question.objects.get(formulario=obj, question_bank__id=question_id).id
                        exclusion_logic_group[str(id_formulario_question)] = exclusion_logic_group.pop(str(question_id))
                        exclusion_logic_group[str(id_formulario_question)][0]["idQuestion"]["id"] = id_formulario_question
                        lista[0]['logic_group'] = exclusion_logic_group

                    if response != None and response != {} :
                        lista[0]['response'] = response
                        if new_url_file:
                            lista[0]['response']['url'] = new_url_file

                    question_data[group].append(lista)
            

        return question_data


class FormularioSerializerList(serializers.ModelSerializer):

    allocating_company = CompanySerializerDetail(read_only=True)
    assigned_company = CompanySerializerDetail(read_only=True)
    period = PeriodSerializer()
    percentage_of_completion = serializers.SerializerMethodField('get_percentage_of_completion')
    percentage_validated = serializers.SerializerMethodField('get_percentage_validated')
    percentage_verified= serializers.SerializerMethodField('get_percentage_verified')


    class Meta:
        model = Formulario
        fields = [ 'id', 'proforestform', 'code_form', 'name', 'created_by',
        'open_date', 'expiration_date', 'validity_period',
        'allocating_company', 'revision_status',
        'status_form',
        'assigned_company',
        'revisor',
        'send_to_company_suply_base', 'period', 'bank_questions', 
        'percentage_of_completion',
        'percentage_validated',
        'percentage_verified',
        ]

    def get_percentage_of_completion(self, obj):
        return obj.percentage_of_completion()

    def get_percentage_validated(self, obj):
        return obj.percentage_of_validated()

    def get_percentage_verified(self,obj):
        return obj.percentage_of_verified()

class FormularioUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Formulario
        fields = [
            'start_date_validation',
            'end_date_validation',
            'revisor',

        ]


class FormularioFeedbackDetailSerializer(serializers.ModelSerializer):

    
    question_package = serializers.SerializerMethodField('get_question_list')

    class Meta:
        model = Formulario
        fields = [
            'id', 'code_form', 'name',
            'question_package',
        ]
    
        
    def get_question_list(self,obj):
        group_dict = obj.proforestform.group_dict
        required_dict = obj.proforestform.required_dict
        language_code = self.context["language_code"]
        exclusion_dict = obj.proforestform.exclusion_dict
        exclusion_logic_group = obj.proforestform.exclusion_logic_group

        question_data ={}
        banderas_file_relationship=[]

        for group in group_dict:
            question_data.setdefault(group,[])
            for question_id in group_dict[group]:
                lista = list(Question.objects.filter(formulario=obj, question_bank__id=question_id).values("id", "question_data", "reviewed_by__email", "validation", "reviewer_observations" ))
                try:
                    lista[0]['required'] = required_dict[str(question_id)]
                except:
                    pass
                    
                try:    
                    response = Question.objects.get(formulario=obj, question_bank__id=question_id).get_response(language=language_code)
                    if response == None:
                        response = Question.objects.filter(answered_by__company=obj.assigned_company, question_bank__id=question_id).order_by('-last_modified')[0].get_response(language=language_code)
                except:
                    response = None
                #exclusion por pregunta
                if str(question_id) in exclusion_dict:
                    array_logica = exclusion_dict[str(question_id)]
                    for element in array_logica:
                        for i, id_dict in enumerate(element['ids']):
                            id_form_question = Question.objects.get(formulario=obj, question_bank__id=id_dict['id']).id
                            id_dict['id'] = id_form_question
                            banderas_file_relationship.append(id_form_question)
                    lista[0]['logic'] = array_logica
                else:
                    form_question = Question.objects.get(formulario=obj, question_bank__id=question_id)
                    if (form_question.id in banderas_file_relationship) and (form_question.question_data['type'] == 'file_upload'):
                        # print("coloca antecedente") #El antecedente es para cuando las preguntas se conectan con un archivo para solo evaluar uno
                        lista[0]['file_exclude'] = True

                #exclusionde grupo
                if str(question_id) in exclusion_logic_group:
                    id_formulario_question = Question.objects.get(formulario=obj, question_bank__id=question_id).id
                    exclusion_logic_group[str(id_formulario_question)] = exclusion_logic_group.pop(str(question_id))
                    exclusion_logic_group[str(id_formulario_question)][0]["idQuestion"]["id"] = id_formulario_question
                    lista[0]['logic_group'] = exclusion_logic_group

                if response != None and response != {} :
                    lista[0]['response'] = response
                question_data[group].append(lista)
                
        return question_data