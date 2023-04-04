from config import settings

from django.db import models
from django.db.models.signals import m2m_changed
from apps.proforestform.models.proforestform import ProforestForm, Period
from apps.company.models.company import Company
from apps.formulario.models.question import Question
from apps.questionsbank.models.questionbank import QuestionBank
from apps.user.models import User

from django.core.mail import EmailMessage

from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.template.loader import render_to_string

from apps.emailcustom.models import EmailTemplate



#Revision of a Proforest-form
NOTASSIGNED = 'NOTASSIGNED'
VERIFIED = 'VERIFIED'
INVERIFYPROCESS = 'INVERIFYPROCESS'
WITHOUTVERIFY = 'WITHOUTVERIFY'
VALIDATE = 'VALIDATE'
INVALIDATINGPROCESS = 'INVALIDATINGPROCESS'
WITHOUTVALIDATE = 'WITHOUTVALIDATE'


REVISION_STATUS_FORM = [
    (VERIFIED, 'verified'),
    (INVERIFYPROCESS, 'in verify process'),
    (WITHOUTVERIFY, 'Without verify'),
    (VALIDATE, 'validated'),
    (INVALIDATINGPROCESS, 'in validadtion process'),
    (WITHOUTVALIDATE, 'Without validate'),
    (NOTASSIGNED, 'Not Asigned')
]

#Status of Proforest Form Internal management trougth Dates plus CRONJOB
NOTVISIBLE = 'NOTVISIBLE'
ACTIVE = 'ACTIVE'
FINISHED = 'FINISHED'
CLOSED = 'CLOSED'

STATUS_FORM = [
    (NOTVISIBLE, 'Not visible form'), 
    (ACTIVE, 'Active Form'),
    (FINISHED, 'Finished Form'),
    (CLOSED, 'Closed Form')
]

#Formulario IS THE MODEL THAT USERS fill

class Formulario(models.Model):

    proforestform = models.ForeignKey(ProforestForm, on_delete = models.PROTECT )
    code_form = models.CharField(max_length=126)
    name = models.CharField(max_length=126)
    created_by = models.ForeignKey(User, on_delete = models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    open_date = models.DateField() # when must be appear active
    expiration_date = models.DateField(blank=True, null=True)# when must be appear closed
    validity_period = models.IntegerField() #On Days
    period = models.ForeignKey(Period, on_delete= models.PROTECT, blank=True, null=True)
    allocating_company = models.ForeignKey(#el dueño que le asigno el form
        Company,
        on_delete = models.PROTECT,
        related_name='allocating_company',
        blank=True, null=True
    )
    revision_status = models.CharField(
        max_length = 64,
        choices = REVISION_STATUS_FORM,
        default = 'NOTASSIGNED'
    )
    status_form = models.CharField(
        max_length=16,
        choices=STATUS_FORM,
        default='NOTVISIBLE'
    )
    assigned_company = models.ForeignKey( #El que lo debe llenar
        Company,
        on_delete = models.PROTECT,
        related_name='assigned_company'
    )

    revisor = models.ManyToManyField(
        User,
        blank=True,
        related_name='revisor_user')
        
    start_date_validation = models.DateField(blank=True, null=True)
    end_date_validation = models.DateField(blank=True, null=True)

    send_to_company_suply_base = models.BooleanField(default=False)
    bank_questions = models.ManyToManyField(QuestionBank)
    status = models.BooleanField(default=True)
    period_code = models.CharField(
        max_length=126,
        blank=True,
        null=True)

    answered_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='formulario_answer_by'
    )
    active_next_period = models.BooleanField(default=True)
    class Meta:
        ordering = ['id']
        permissions=[
            ("fill_out_forms", "Can fill formulario"),
            ("assign_forms", "Can asign formulario"),

        ]
    def __str__(self):
        return str(f"{self.id}. form code: {self.code_form}" )
    
    def total_questions_with_group_exclusion(self, *args):
        
        exclusion_logic_group = self.proforestform.exclusion_logic_group
        if exclusion_logic_group == {} :#no tiene logica exclusion cuente normal
            # print("<<<< NO HABIA LOGICA EXCLUSION POR GRUPO")
            total_questions = Question.objects.filter(formulario=self, status=True).count()
            
        else:
            # print(">>>SI TENIA EXCLUSION POR LOGICA DE GRUPO", exclusion_logic_group)
            total_questions = Question.objects.filter(formulario=self, status=True).count()
            for key, value in exclusion_logic_group.items():
                try:
                    answer = Question.objects.get(formulario=self, question_bank__id=key).answer
                    answer_value = list(answer.values())[0] # Just capture the answer value
                    value_dict = value[0]['option'][0]['id']
                    # print("VALUE_DICT ", value_dict)
                    # print("ANSWER_VALUE ", answer_value)

                    condition = value[0]['condition']['id']
                    expresion = 'answer_value ' + condition + ' value_dict'
                    if eval(expresion):
                        group_exclude = value[0]['source_groups']
                        descuento = len(self.proforestform.group_dict[str(group_exclude)])
                        total_questions = total_questions - descuento
                    else:
                        pass
                except:
                    pass
                        

        return total_questions

    def percentage_of_completion(self, *args):
        questions = self.total_questions_with_group_exclusion()
        questions_fill = Question.objects.filter(formulario=self, status=True).exclude(answered_by = None).count()

        try:
            return round((questions_fill * 100)/questions)
        except:
            return 0

    def assigned_form_email(self ):
        users_emails = list(User.objects.filter(company = self.assigned_company).values_list('email', flat=True))
        try:
            EmailTemplate.send(
                'new_form_assigned',
                {
                    'form_name': self.name,
                    'allocating_company': self.allocating_company,
                    'assigned_company': self.assigned_company,
                    'expiration_date': self.expiration_date.strftime('%d/%m/%Y'),
                },
                emails = users_emails, 
            )
        except:
            print("Email for form no sended", self)
        

    def assigned_new_user_form_email(self, email_responsable, slug ):
        users_emails = [email_responsable]
        EmailTemplate.send(
            'new_user_form_assigned',
            {
                'form_name': self.name,
                'assigned_company': self.assigned_company,
                'expiration_date': self.expiration_date.strftime('%d/%m/%Y'),
                'slug_key': slug,
                'id_company': self.assigned_company.id,
                'name_company': self.assigned_company.name,
                'email_user': email_responsable,

            },
            emails = users_emails,
        )
    
    def validate_form_email(self ):
        users_emails = [self.created_by.email, self.proforestform.created_by.email]

        EmailTemplate.send(
            'validate_form_resume',
            {
                'form_name': self.name,
                'name_assigned_form': self.created_by.get_full_name(),
                'name_creator_proforestform': self.proforestform.created_by.get_full_name(),
                'allocating_company': self.allocating_company,
                'assigned_company': self.assigned_company,
                'number_questions': self.number_questions(),
                'percentage_of_validated': self.percentage_of_validated(),
                
            },
            emails = users_emails,
        )
    
    def validate_info_assigned_company(self ):
        users_emails = [self.answered_by.email]
        EmailTemplate.send(
            'validate_info_assigned_company',
            {
                'form_name': self.name,
                'answered_by':self.answered_by.get_full_name(),
                'allocating_company': self.allocating_company,
                'assigned_company': self.assigned_company,
                'number_questions': self.number_questions(),
                'percentage_of_validated': self.percentage_of_validated(),
                'period_code': self.period_code
            },
            emails = users_emails,
        )

    def verificate_form_email(self ):
        users_emails = [self.created_by.email, self.proforestform.created_by.email]
        EmailTemplate.send(
            'verificate_form_resume',
            {
                'form_name': self.name,
                'name_assigned_form': self.created_by.get_full_name(),
                'name_creator_proforestform': self.proforestform.created_by.get_full_name(),
                'allocating_company': self.allocating_company,
                'assigned_company': self.assigned_company,
                'number_questions': self.number_questions(),
                'percentage_of_verified': self.percentage_of_verified(),
            },
            emails = users_emails,
        )

    def verificate_info_assigned_company(self ):
        users_emails = [self.answered_by.email]
        EmailTemplate.send(
            'verificate_info_assigned_company',
            {
                'form_name': self.name,
                'answered_by':self.answered_by.get_full_name(),
                'allocating_company': self.allocating_company,
                'assigned_company': self.assigned_company,
                'number_questions': self.number_questions(),
                'percentage_of_verified': self.percentage_of_verified(),
                'period_code': self.period_code
            },
            emails = users_emails,
        )

    def number_questions(self, *args):
        questions_number = Question.objects.filter(formulario=self).count()
        return questions_number

    def percentage_of_validated(self, *args):
        questions = Question.objects.filter(formulario=self).count()
        questions_validated = Question.objects.filter(formulario=self, validation = 'VAL').count()
        questions_verified = Question.objects.filter(formulario=self, validation = 'VER').count()

        try:
            return round((((questions_validated+questions_verified) * 100)/questions))
        except:
            return 0
    
    def percentage_of_verified(self, *args):
        questions = Question.objects.filter(formulario=self).count()
        questions_verified = Question.objects.filter(formulario=self, validation = 'VER').count()
        try:
            return round(((questions_verified * 100)/questions))
        except:
            return 0


    

def formulario_bankquestion_added(sender, **kwargs): #Always when a new FORM saves, it updates hiw own questions
    formulario = kwargs.get('instance')
    for incoming_question in formulario.bank_questions.all():
        #Valido si existe Question 
        if Question.objects.filter(question_bank=incoming_question, formulario= formulario).exists():
            form_question = Question.objects.get(question_bank=incoming_question, formulario= formulario)
            form_question.status= True
            try:
                form_question.required = formulario.proforestform.required_dict[str(incoming_question.id)]
            except:
                form_question.required = False #if not required

            form_question.save()
        else:
            Question.objects.create(
                formulario = formulario,
                question_bank = incoming_question,
                question_data = incoming_question.question_data,
                required = formulario.proforestform.required_dict[str(incoming_question.id)]
            )

    active_form_questions = Question.objects.filter(formulario= formulario, status=True)    
    for active_question in active_form_questions:
        if not active_question.question_bank in formulario.bank_questions.all():
            active_question.status=False
            active_question.save()
    return 

m2m_changed.connect(formulario_bankquestion_added, sender=Formulario.bank_questions.through)

import math

@receiver(pre_save, sender=Formulario)
def make_period_code(sender, **kwargs):
    instance = kwargs.get('instance')
    if not instance.period_code:
        open_date_year = instance.open_date.year
        open_date_month = instance.open_date.month
        period_code = instance.period.code
        period_months = instance.period.months
        periodo = math.ceil(open_date_month/period_months)
        instance.period_code = period_code+'-'+str(periodo)+'-'+str(open_date_year)
    return


class ValidateFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_validation = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a validacion del formulario
        max_length=3,
    )
    class Meta:
        permissions =[
            ("assign_validation_formulario", "Can assign validation formulario"),
        ]

class VerifyFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_verification = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a la verificacion del formulario
        max_length=3,
    )

    class Meta:
        permissions =[
            ("assign_verification_formulario", "Can assign verification formulario"),
        ]