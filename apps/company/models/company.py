from cities_light.models import Country, Region, SubRegion
from apps.utils.models import base_model
from apps.user.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models.signals import post_save


from .commodity import Commodity
from .actor_type import ActorType
from .company_group import CompanyGroup

import uuid
import requests
import json

class Company(base_model.BaseModel):

    name = models.CharField(max_length=126)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        blank=True,
        null=True
        )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        SubRegion,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    identifier_global_company = models.CharField(
        max_length=126,
        blank=True,
        null=True,
        unique=True,
    )
    identifier_proforest_company = models.CharField(
        max_length=126,
        blank=True,
        null=True,
        unique=True,
    )
    nit = models.CharField(max_length=126)
    commodity = models.ForeignKey(
        Commodity,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    actor_type = models.ForeignKey(
        ActorType,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    company_group = models.ForeignKey(
        CompanyGroup,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    validator_user = models.ManyToManyField(
        User,
        related_name='validator',
        blank=True,
    )
    has_responsable = models.BooleanField(default=False)
    has_superuser = models.BooleanField(default=False)


    class ProfileCompany(models.TextChoices):
        SUPPLIERCLIENT = 'SC', _('Suplier Client')
        PROFORESTCLIENT = 'PC', _('Proforest Client')
        SUPPLIERCLIENTOTHERS = 'SO', _('Suplier Client Other')

    company_profile = models.CharField(
        max_length=2,
        choices=ProfileCompany.choices,
        blank=True
    )

    deadline_validation = models.DateField(blank=True, null=True)
    class CompanyValidated(models.TextChoices):
        SELFREPORTED = 'SR', _('Self Reported')
        NOTVALIDATED = 'NV', _('Not Validated')
        VALIDATED = 'VA', _('Validated')
        NOTVERIFY = 'NVE', _('Not Verified')
        VERIFIED = 'VE', _('Verified')


    status_revision = models.CharField( # Respecto al estado del validador si se asigna NR si ya lo reviso pendiente IP  o ya reviso RE
        max_length=3,
        choices=CompanyValidated.choices,
        default=CompanyValidated.SELFREPORTED,
        blank=True
    )

    note_revision = models.TextField(blank=True, null=True)
    start_date_validation = models.DateField(blank=True, null=True)
    end_date_validation = models.DateField(blank=True, null=True)

    drive_folder_id = models.CharField(max_length = 126, blank=True, null=True)
   


    class Meta:
        ordering = ['name']
        permissions =[
            ("update_own_company", "Can Update his own Company"),
        ]

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.latitude = round(self.latitude, 8) if self.latitude else None
        self.longitude = round(self.longitude, 8) if self.longitude else None
        return super(Company, self).save(*args, **kwargs)



@receiver(pre_save, sender=Company)
def create_proforest_code(sender, **kwargs):
    instance = kwargs.get('instance')
    abc = ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
           "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    if ProforestCode.objects.exists():
        pkey = ProforestCode.objects.latest('id').pk + 1
    else:
        pkey = 1

    if not instance.identifier_global_company:  # HU-004
        type_actor = instance.actor_type.proforest_actortype_code
        commodity = instance.commodity.proforest_commodity_code
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

        identifier_proforest_company = str(type_actor+commodity+'-'+code)
        instance.identifier_global_company = identifier_proforest_company
        instance.identifier_proforest_company = identifier_proforest_company
        ProforestCode.objects.create(name=str(identifier_proforest_company))
        return

    else:
        instance.identifier_proforest_company = instance.identifier_global_company
        instance.identifier_global_company = instance.identifier_proforest_company
        return

@receiver(post_save, sender=Company)
def create_folder_onedrive(sender, **kwargs):
    from apps.onedrive.models import Token
    instance = kwargs.get('instance')
    if (instance.drive_folder_id == None or instance.drive_folder_id == ''):
        
        drive_actor_type = instance.actor_type.drive_folder_id
        URL_ONEDRIVE = f'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/items/{drive_actor_type}/children'
       
        token = Token.objects.latest()
        data = {
            "name": f'{instance.identifier_proforest_company.strip()}_{instance.name.strip()}_',
            "folder": {}
        }  # JSON data as a string
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token.access_token
            }
        response = requests.post(URL_ONEDRIVE, data=json.dumps(data), headers=headers)
        result = response.json()
        instance.drive_folder_id = result['id']
        instance.save()# i got the folder saved
    else:
        pass
    return

class ProforestCode(base_model.BaseModel):
    name = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return str(self.pk)


class CompanyUserFormKey(base_model.BaseModel):
    company = models.ForeignKey(Company, on_delete = models.DO_NOTHING)
    email = models.EmailField()
    slug = models.SlugField(unique=True, blank= True)

@receiver(pre_save, sender=CompanyUserFormKey)
def slug_handler(sender, **kwargs):
    instance = kwargs.get('instance')

    if not instance.slug:
        for _ in range(16):
            slug = uuid.uuid4()

            if not sender.objects.filter(slug=slug).exists():
                instance.slug = slug
                return

class ValidateCompany(models.Model):
    company = models.ForeignKey(Company, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_validation = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a la geolocalizacion de la company
        max_length=3,
    )
    class Meta:
        permissions =[
            ("assign_validation_company", "Can assign validation company"),
        ]

class VerifyCompany(models.Model):
    company = models.ForeignKey(Company, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_verification = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a la geolocalizacion de la company
        max_length=3,
    )
    class Meta:
        permissions =[
            ("assign_verification_company", "Can assign verification company"),
        ]


from apps.questionsbank.models.category import Category
from apps.questionsbank.models.subcategory import SubCategory

class QuestionDriveCategoryFolder(base_model.BaseModel):

    company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT
        )
    category = models.ForeignKey(
        Category,
        on_delete = models.PROTECT
        )
    drive_folder_category_id = models.CharField(max_length = 126, blank=True, null=True)

class QuestionDriveSubCategoryFolder(base_model.BaseModel):

    company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT
        )
    category = models.ForeignKey(
        Category,
        on_delete = models.PROTECT
        )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete = models.PROTECT
        )
    drive_folder_subcategory_id = models.CharField(max_length = 126, blank=True, null=True)
