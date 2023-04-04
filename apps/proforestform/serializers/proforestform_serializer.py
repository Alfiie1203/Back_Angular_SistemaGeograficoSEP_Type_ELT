from rest_framework import serializers
from ..models.proforestform import ProforestForm
from ..serializers.period_serializer import PeriodSerializer
from django.http import JsonResponse
from apps.proforestform.models.proforestform import QuestionBank
from django.core.paginator import Paginator

class ProforestFormSerializerList(serializers.ModelSerializer):
    period = PeriodSerializer()
    class Meta:
        model = ProforestForm
        fields = [ 'id', 'version', 'code_form', 'name', 'created_by',
        # 'collaborators', 
        'open_date', 'expiration_date', 'reported_period', 'validity_period',
        'period',
        # 'bank_questions', 
        ]

class ProforestFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProforestForm
        fields = [ 'id', 'version', 'code_form', 'name', 'created_by',
        # 'collaborators', 
        'open_date', 'expiration_date', 'reported_period', 'validity_period',
        'period',
        # 'name_group', 
        ]

class ProforestFormUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProforestForm
        fields = [ 'name', 'open_date', 'expiration_date', 'reported_period', 'validity_period', 'period',
        # 'name_group', 
        # 'collaborators', 'bank_questions',
         ]

class ProforestFormDetailBankSerializer(serializers.ModelSerializer):

    question_package = serializers.SerializerMethodField('get_question_list')
    next = serializers.SerializerMethodField('get_next_page')
    back = serializers.SerializerMethodField('get_back_page')


    class Meta:
        model = ProforestForm
        fields = [
            'next',
            'back',
            'id', 'code_form', 'name', 'created_by', 'collaborators', 
            'open_date', 'expiration_date', 'validity_period', 'period',
            'bank_questions','version',
            'question_package',
            
        ]
    def get_question_list(self,obj):
        pagination= self.context["pagination"]
        page= self.context["page"]
        questions = obj.bank_questions.all().order_by('id')
        if pagination != None and page != None:
            p = Paginator(questions, pagination)
            questions = p.page(page).object_list
 
        return questions.values("id", "type", "category", "subcategory", "topic", "question_data" )

    def get_next_page(self,obj):
        pagination= self.context["pagination"]
        page= self.context["page"]
        path= self.context["path"]
        questions = obj.bank_questions.all().order_by('id')
        if pagination != None and page != None:
            p = Paginator(questions, pagination)
            if p.page(page).has_next():
                next_page = int(page)+1
                return path.split('?',1)[0]+f'?pagination={pagination}&page={next_page}'
        return f''

    def get_back_page(self,obj):
        pagination= self.context["pagination"]
        page= self.context["page"]
        path= self.context["path"]

        questions = obj.bank_questions.all().order_by('id')
        if pagination != None and page != None:
            p = Paginator(questions, pagination)
            if p.page(page).has_previous():
                back_page = int(page) - 1
                return path.split('?',1)[0]+f'?pagination={pagination}&page={back_page}'
        return f''

class ProforestFormDetailSerializer(serializers.ModelSerializer):
    group_logic = serializers.SerializerMethodField('get_grouplogic')
    question_package = serializers.SerializerMethodField('get_question_list')
    collaborators = serializers.SerializerMethodField('get_collaborators_list')
    period = PeriodSerializer()

    class Meta:
        model = ProforestForm
        fields = [
            'id', 'code_form', 'name', 'created_by',  
            'open_date', 'expiration_date', 'validity_period', 'period',
            'bank_questions','version',
            'collaborators',
            'question_package',
            'group_logic',
            'name_group'
            
        ]

    def get_question_list(self,obj):
        group_dict = obj.group_dict
        required_dict = obj.required_dict
        exclusion_dict = obj.exclusion_dict
        exclusion_logic_group = obj.exclusion_logic_group
        question_data ={}

        for group in group_dict:
            question_data.setdefault(group,[])
            for question_id in group_dict[group]:
                lista =  list(QuestionBank.objects.filter(id=question_id).values("id", "question_data" ))
                lista[0]['required'] = required_dict[str(question_id)]
                if str(question_id) in exclusion_dict:
                    lista[0]['logic'] = exclusion_dict[str(question_id)]

                if (exclusion_logic_group != None) and (str(question_id) in exclusion_logic_group):
                    lista[0]['logic_group'] = exclusion_logic_group
                
                question_data[group].append(lista)
            
        return question_data

    def get_collaborators_list(self,obj):
        collaborators = obj.collaborators.all()
        list_collaborators = []
        
        for collaborator in collaborators:
            list_collaborators.append({
                'id': collaborator.id,
                'full_name': collaborator.get_full_name()
            })

        return list_collaborators

    def get_grouplogic(self,obj):
        exclusion_logic_group = obj.exclusion_logic_group
        logic_group_data = []
        #Marco si este grupo alguien lo oculta

        for key, value in  exclusion_logic_group.items():
            lista = []
            for sub_val in value:
                condicion = sub_val
                # condicion['id_que']=condicion.pop('groups')
                condicion['id_question']= key
            logic_group_data.append(condicion)
        return logic_group_data
            
                