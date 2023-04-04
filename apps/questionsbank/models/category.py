from django.db import models
from apps.utils.models import base_model
from django.dispatch import receiver
from django.db.models.signals import post_save


class Category(base_model.BaseModel):
    name_en = models.CharField(max_length=126, unique=True)
    name_es = models.CharField(max_length=126, unique=True)
    name_pt = models.CharField(max_length=126, unique=True)
    code = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return str(self.name_en)

@receiver(post_save, sender=Category)
def update_subcategory_status(sender, **kwargs):
    from apps.questionsbank.models.subcategory import SubCategory #avoid circular importation
    instance = kwargs.get('instance')
    subcategories = SubCategory.objects.filter(category=instance)
    for subcategory in subcategories:
        subcategory.status = instance.status
        subcategory.save()
    return