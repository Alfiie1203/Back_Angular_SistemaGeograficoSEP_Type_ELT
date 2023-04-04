from django.db import models
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver

from apps.questionsbank.models.questionbank import QuestionBank
from apps.user.models import User
from apps.utils.models import base_model
from apps.company.models.company import Company

from apps.emailcustom.models import EmailTemplate

import time 

#Revision of a Proforest-form
CHECKED = 'CHECK'
INPROCESS = 'INPROCESS'
WITHOUTCHEKING = 'WITHOUTCHECK'

REVISION_STATUS_FORM = [
    (CHECKED, 'Checked'),
    (INPROCESS, 'in process'),
    (WITHOUTCHEKING, 'Without checking'),
]

#Status of Proforest Form Internal management trougth Dates plus CRONJOB
NOTVISIBLE = 'NOTVISIBLE'
ACTIVE = 'ACTIVE'
CLOSED = 'CLOSED'

STATUS_FORM = [
    (NOTVISIBLE, 'Not visible form'), 
    (ACTIVE, 'Active Form'),
    (CLOSED, 'Closed Form')
]
class Period(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=64)
    months = models.IntegerField() #Number of months

    def __str__(self):
        return str(self.name)

class ProforestForm(models.Model):
    
    code_form = models.CharField(max_length=126, blank=True, null=True)
    name = models.CharField(max_length=126)
    created_by = models.ForeignKey(User, on_delete = models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    collaborators = models.ManyToManyField(
        User,
        related_name='User_collaborators',
        blank=True
    )
    open_date = models.DateField() # when must be appear active
    expiration_date = models.DateField(blank=True, null=True)# when must be appear closed
    reported_period = models.DateField(blank=True, null=True) # It shows about the period of reporting
    validity_period = models.IntegerField() #On Days
    period = models.ForeignKey(Period, on_delete= models.PROTECT, blank=True, null=True)
    bank_questions = models.ManyToManyField(QuestionBank)
    group_dict = models.JSONField(blank=True, null=True)
    required_dict = models.JSONField(blank=True, null=True)
    exclusion_dict = models.JSONField(blank=True, null=True)
    exclusion_logic_group = models.JSONField(blank=True, null=True)
    name_group = models.JSONField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    status = models.BooleanField(default=True)
    data = models.JSONField(blank=True, null=True) #Aca va el JSON del versionado del proforestForm
    #llave para saber quien lo puede asignar
    company_assigned = models.ManyToManyField( #O compañias asignadas para saber quien lo puede mandarlo a llenar
        Company,                    #las compañias son solo las que tienen superuser activo
        related_name='Company_assigned',
        blank=True
    )

    def __str__(self):
        return str(f"ProforestForm-{self.id}-code{self.code_form}" )

def proforestform_questionbank_add(sender, **kwargs): #Always when a new PROFORESTFORM saves, it updates hiw own forms
    from apps.formulario.models.formulario import Formulario
    proforestform = kwargs.get('instance')
    #SEARCH FORMS without close or finished
    formularios = Formulario.objects.filter(proforestform = proforestform).exclude(status_form='FINISHED').exclude(status_form='CLOSED')
    for formulario in formularios:
        formulario.bank_questions.set(proforestform.bank_questions.all()) 
        formulario.save()

    return 

m2m_changed.connect(proforestform_questionbank_add, sender=ProforestForm.bank_questions.through)

@receiver(pre_save, sender=ProforestForm)
def create_proforest_code(sender, **kwargs):
    instance = kwargs.get('instance')
    abc = ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
           "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    if ProforestFormCode.objects.exists():
        pkey = ProforestFormCode.objects.latest('id').pk + 1
    else:
        pkey = 1

    if not instance.code_form:  # Reunion 7Dic
        iniciales = "FORM"
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

        proforestform_code = str(iniciales+'-'+code)
        instance.code_form = proforestform_code
        ProforestFormCode.objects.create(name=str(proforestform_code))
        return

    else:
        instance.code_form = instance.code_form
        return

class ProforestFormCode(base_model.BaseModel):
    name = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return str(self.pk)

#function that notifi to new collaborators added
@receiver(m2m_changed, sender=ProforestForm.collaborators.through)
def notify_new_collaborators(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        #traigo la instancia de nuevos collaboradores
        new_collaborators = instance.collaborators.filter(pk__in=pk_set)
        #send an email to each new collaborator
        for collaborator in new_collaborators:
            user_email_as_list = [collaborator.email]
            EmailTemplate.send(
            'assigned_as_collaborator_in_form',
            {
                'form_name': instance.name,
                'collaborator_name': collaborator.get_full_name()
            },
            emails = user_email_as_list, 
            )
            time.sleep(1)
m2m_changed.connect(notify_new_collaborators, sender=ProforestForm.collaborators.through)

