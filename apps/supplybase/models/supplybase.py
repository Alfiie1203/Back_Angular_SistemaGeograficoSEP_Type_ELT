from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.user.models import User
from apps.company.models.company import Company
from apps.proforestform.models.proforestform import ProforestForm
from apps.company.models.actor_type import ActorType


class SupplyBase (models.Model):
    company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT,
        related_name='supplybase_company',
    )
    supplier_company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT,
        related_name='supplybase_supplier_company',
    )

    created = models.DateTimeField(auto_now_add=True)

    def get_some_fill_form(self):
        #Search if supplier company has filled forms
        if ProforestForm.objects.filter(assigned_company=self.supplier_company, revision_status='CHECK' ).exists():
            return True
        else:
            return False

    def get_fill_form_for_my_company(self):
        #Search if supplier company has filled my sended forms

        if ProforestForm.objects.filter(
                    allocating_company=self.company,
                    assigned_company=self.supplier_company,
                    revision_status='CHECK' ).exists():
            return True
        else:
            return False

class SupplyBaseDependency (models.Model):
    actor_type = models.OneToOneField(
        ActorType,
        on_delete=models.PROTECT,
        related_name='actortype_buyer',
    )
    actor_type_dependency = models.ManyToManyField(ActorType)

class SupplyBaseRegister(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='register_by')
    company = models.ForeignKey(
        Company,
        on_delete = models.PROTECT,
        related_name='reporting_company',
    )
    register_year =  models.IntegerField()
    period = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)])
    purchased_volume = models.FloatField(blank = True, null = True) #Lo que compro para ese periodo en volumen (toneladas)

    def __str__(self):
        return str(self.company) + ' Year: '+ str(self.register_year) +' period: '+ str(self.period)

class PurchasedPercentage(models.Model):
    supplybase_register = models.ForeignKey(
        SupplyBaseRegister,
        on_delete=models.PROTECT,
    )
    percentage = models.FloatField()
    actor_type = models.ForeignKey(
        ActorType,
        on_delete=models.PROTECT,
        related_name='supplier_actortype',
    )