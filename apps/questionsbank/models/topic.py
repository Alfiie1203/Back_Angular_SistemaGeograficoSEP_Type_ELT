from email.mime import base
from django.db import models
from .subcategory import SubCategory
from apps.utils.models import base_model
from django.dispatch import receiver
from django.db.models.signals import post_save



class Topic(base_model.BaseModel):
    subcategory = models.ForeignKey(
        SubCategory,
        related_name='topic',
        on_delete=models.PROTECT,

    )
    name_en = models.CharField(max_length=126)
    name_es = models.CharField(max_length=126)
    name_pt = models.CharField(max_length=126)
    code = models.CharField(max_length=126, unique=True)

    def __str__(self):
        return str(self.subcategory) +'_' + str(self.name_es)

@receiver(post_save, sender=Topic) #update Status of questions
def update_questionbank_status(sender, **kwargs):
    from apps.questionsbank.models.questionbank import QuestionBank #avoid circular importation
    instance = kwargs.get('instance')
    questions = QuestionBank.objects.filter(topic=instance)
    for question in questions:
        question.status = instance.status
        question.save()
    return