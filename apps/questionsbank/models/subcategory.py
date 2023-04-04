from email.mime import base
from django.db import models
from apps.utils.models import base_model
from .category import Category
from django.dispatch import receiver
from django.db.models.signals import post_save



class SubCategory(base_model.BaseModel):
    category = models.ForeignKey(
        Category,
        related_name='subcategory',
        on_delete=models.PROTECT
    )
    name_en = models.CharField(max_length=126)
    name_es = models.CharField(max_length=126)
    name_pt = models.CharField(max_length=126)
    code = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return str(self.name_es)

@receiver(post_save, sender=SubCategory)
def update_topic_status(sender, **kwargs):
    from apps.questionsbank.models.topic import Topic #avoid circular importation
    instance = kwargs.get('instance')
    topics = Topic.objects.filter(subcategory=instance)
    for topic in topics:
        topic.status = instance.status
        topic.save()
    return