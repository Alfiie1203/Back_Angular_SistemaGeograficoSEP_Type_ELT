from enum import auto
from django.db import models
from cities_light.models import Country, Region, SubRegion
from apps.utils.models import base_model
from apps.user.models import User
from apps.company.models.company import Company
from apps.company.models.company_group import CompanyGroup
from apps.company.models.commodity import Commodity
from apps.company.models.actor_type import ActorType
from apps.proforestform.models.proforestform import Period

from apps.supplybase.models.supplybase import SupplyBase
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _




class TraceabilityFile(models.Model):
    upload_by = models.ForeignKey(
        User,
        on_delete = models.PROTECT,
        related_name='reporting_user',

    )
    reporting_company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT,
        related_name='company_file',
        null=True,
        blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    file_traceability = models.FileField(upload_to='traceabilityfiles/%Y/%m')
    

class Traceability(models.Model):

    reported_user = models.ForeignKey(
        User,
        on_delete = models.PROTECT,
        related_name='reported_user',

    )
    reported_company = models.ForeignKey( #Compania que hace el reporte
        Company,
        on_delete = models.PROTECT,
        related_name='reported_company',
    )
    supplier_company = models.ForeignKey( #Compania que suministro el tema
        Company,
        on_delete = models.PROTECT,
        related_name='supplier_company',
    )
    commodity = models.ForeignKey(
        Commodity,
        on_delete = models.PROTECT,
    )
    actor_type = models.ForeignKey(
        ActorType,
        on_delete = models.PROTECT
    )
    company_group = models.ForeignKey(
        CompanyGroup,
        on_delete = models.PROTECT,
        blank=True,
        null=True,
    )
    date_reported = models.DateTimeField(auto_now_add=True)
    supplier_name = models.CharField(max_length = 126, blank = True, null = True)
    supplier_tax_number = models.CharField(max_length = 126, blank = True, null = True)
    supplier_capacity = models.FloatField(blank = True, null = True) #Lo que puede producir
    supplier_production = models.FloatField(blank = True, null = True) #Lo que produjo
    purchased_volume = models.FloatField(blank = True, null = True) #Lo que Compro en tons
    certification = models.CharField(max_length = 126, blank = True, null = True)
    latitude = models.FloatField(blank = True, null = True)
    longitude = models.FloatField(blank = True, null = True)
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
    year = models.IntegerField()
    period = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)])

    class TraceabilityValidate(models.TextChoices):
        SELFREPORTED = 'SR', _('Self Reported')
        NOTVALIDATED = 'NV', _('Not Validated')
        VALIDATED = 'VA', _('Validated')
        NOTVERIFIED = 'NVE', _('Not Verified')
        VERIFIED = 'VE', _('Verified')

    status_revision = models.CharField(   # respecto a la geolocalizacion de la trazabilidad
        max_length=3,
        choices=TraceabilityValidate.choices,
        default=TraceabilityValidate.SELFREPORTED,
    )

    validator_user = models.ManyToManyField(
        User,
        related_name='validator_traceability',
        blank=True,
    )
    start_date_validation = models.DateField(blank=True, null=True)
    end_date_validation = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-pk']
        permissions =[
            ("export_traceability", "Can export traceability"),
        ]
    
    def save(self, *args, **kwargs):
        self.latitude = round(self.latitude, 8)
        self.longitude = round(self.longitude, 8)
        return super(Traceability, self).save(*args, **kwargs)

@receiver(post_save, sender = Traceability)
def create_suply_base_register(sender, **kwargs):
    instance = kwargs.get('instance')
    company = instance.reported_company
    supplier_company = instance.supplier_company

    if not SupplyBase.objects.filter(company=company, supplier_company=supplier_company).exists():
        SupplyBase.objects.create(company=company, supplier_company=supplier_company)

    return

class ValidateTraceability(models.Model):
    traceability = models.ForeignKey(Traceability, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_validation = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a la geolocalizacion de la trazabilidad
        max_length=3,
    )

    # class Meta:
    #     permissions =[
    #         ("assign_validation_traceability", "Can assign validation traceability"),
    #     ]

class VerifyTraceability(models.Model):
    traceability = models.ForeignKey(Traceability, on_delete= models.PROTECT)
    message = models.TextField()
    autor = models.ForeignKey(User, on_delete= models.PROTECT)
    date_verification = models.DateTimeField(auto_now_add=True)
    status_revision = models.CharField(   # respecto a la geolocalizacion de la trazabilidad
        max_length=3,
    )
    # class Meta:
    #     permissions =[
    #         ("assign_verification_traceability", "Can assign verify traceability"),
    #     ]