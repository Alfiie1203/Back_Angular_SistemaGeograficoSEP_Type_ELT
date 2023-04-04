from django.db import models
from apps.utils.models import base_model
from apps.questionsbank.models.questionbank import QuestionBank
from apps.user.models import User

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

import requests
import json

class Question(base_model.BaseModel):

    AUTOREPORTED = 'ARE'
    VALIDATED = 'VAL'
    NOTVALIDATED = 'NVA'
    VERIFIED = 'VER'
    NOTVERIFIED = 'NVE'
    VALIDATIONS = [
        (AUTOREPORTED, 'Autoreported answer'),
        (VALIDATED, 'Validated answer'),
        (NOTVALIDATED, 'Not validated answer'),
        (VERIFIED, 'Verified answer'),
        (NOTVERIFIED, 'Not Verified answer'),
    ]

    formulario = models.ForeignKey(
        'formulario.Formulario',
        on_delete = models.PROTECT,
        blank=True,
        null=True,
    )
    question_bank = models.ForeignKey(
        QuestionBank,
        on_delete = models.PROTECT,
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='reviewed_user'
    )
    answered_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='answer_by'
    )
    reviewer_observations =  models.TextField(blank=True, null=True)
    validation = models.CharField(
        max_length = 3,
        choices = VALIDATIONS,
        default='ARE'
    )
    question_data= models.JSONField(blank=True, null=True)
    group = models.CharField(max_length=16)
    answer = models.JSONField(blank=True, null=True)
    required = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return str(f"Question-{self.id} of form {self.formulario.code_form}")

    def get_response(self, language):
        try:
            if self.question_data['type'] == 'open_answer':
                return self.answer

            elif self.question_data['type'] == 'select_one':
                answer = self.answer
                for index in answer:
                    return answer[index][language]

            elif self.question_data['type'] == 'select_multiple':
                response = []
                answer = self.answer
                for row in answer:
                    for index in row:
                        response.append(row[index][language])
                return response

            elif self.question_data['type'] == 'matrix_select_multiple':
                response = {}
                answer = self.answer
                for row in answer:
                    question = row[0][language]
                    respuesta = row[1][language]
                    response.setdefault(question,[]).append(respuesta)
                return response

            elif self.question_data['type'] == 'matrix_select_one':
                if self.question_data['appearance'] == 'radio':
                    response = {}
                    answer = self.answer
                    for row in answer:
                        question = row[0][language]
                        respuesta = row[1][language]
                        response[question]=respuesta
                elif self.question_data['appearance'] == 'dropdown_list':
                    response = {}
                    answer = self.answer
                    response = {}
                    for a in answer:
                        location = str(a[0]+'_'+a[1])
                        respuesta = a[2][language]
                        response[location]=respuesta

                else:
                    response = {}
                    answer = self.answer
                    for row in answer:
                        question = row[0][language]
                        respuesta = row[1][language]
                        response.setdefault(question,[]).append(respuesta)
                return response
            elif self.question_data['type'] == 'file_upload':
                return self.answer
                
            else:
                return None
                # return str("No terminado")
        except:
            return None

@receiver(post_save, sender=Question)
def create_folder_onedrive(sender, **kwargs):
    from apps.onedrive.models import Token
    from apps.company.models.company import QuestionDriveCategoryFolder, QuestionDriveSubCategoryFolder
    instance = kwargs.get('instance')
    if instance.question_data['type'] == 'file_upload':
        company = instance.formulario.assigned_company
        category = instance.question_bank.category
        subcategory = instance.question_bank.subcategory

        if not (QuestionDriveCategoryFolder.objects.filter(company=company, category=category).exists()):
            #create la categoria para esa compañia
            drive_company = company.drive_folder_id
            URL_ONEDRIVE = f'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/items/{drive_company}/children'
        
            token = Token.objects.latest()
            data = {
                "name": f'{category.name_es.strip()}',
                "folder": {}
            }  # JSON data as a string
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.access_token
                }
            response = requests.post(URL_ONEDRIVE, data=json.dumps(data), headers=headers)
            result = response.json()
            questiondrivecategoryfolder = QuestionDriveCategoryFolder.objects.create(
                company = instance.formulario.assigned_company,
                category = instance.question_bank.category,
                drive_folder_category_id = result['id']
            )
        else:
            questiondrivecategoryfolder = QuestionDriveCategoryFolder.objects.get(company=company, category=category)

        if not (QuestionDriveSubCategoryFolder.objects.filter(company=company, category=category, subcategory=subcategory).exists()):
            #create la sub-categoria para esa compañia
            drive_company_category = questiondrivecategoryfolder.drive_folder_category_id
            URL_ONEDRIVE = f'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/items/{drive_company_category}/children'
        
            token = Token.objects.latest()
            data = {
                "name": f'{subcategory.name_es.strip()}',
                "folder": {}
            }  # JSON data as a string
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token.access_token
                }
            response = requests.post(URL_ONEDRIVE, data=json.dumps(data), headers=headers)
            result = response.json()
            questiondrivesubcategoryfolder = QuestionDriveSubCategoryFolder.objects.create(
                company = instance.formulario.assigned_company,
                category = instance.question_bank.category,
                subcategory = instance.question_bank.subcategory,
                drive_folder_subcategory_id = result['id']
            )
        else:
            questiondrivesubcategoryfolder = QuestionDriveSubCategoryFolder.objects.get(company=company, category=category, subcategory=subcategory)
            
    return

           
class QuestionHistory(models.Model):
    AUTOREPORTED = 'ARE'
    VALIDATED = 'VAL'
    NOTVALIDATED = 'NVA'
    VERIFIED = 'VER'
    NOTVERIFIED = 'NVE'
    VALIDATIONS = [
        (AUTOREPORTED, 'Autoreported answer'),
        (VALIDATED, 'Validated answer'),
        (NOTVALIDATED, 'Not validated answer'),
        (VERIFIED, 'Verified answer'),
        (NOTVERIFIED, 'Not Verified answer'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    validation = models.CharField(
        max_length = 3,
        choices = VALIDATIONS
    )
    question = models.ForeignKey(
        Question,
        on_delete = models.PROTECT
        )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='reviewed_comment_user'
    )
    reviewer_observations =  models.TextField(blank=True, null=True)

    answered_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='answer_question_by'
    )
    answer = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-id']


