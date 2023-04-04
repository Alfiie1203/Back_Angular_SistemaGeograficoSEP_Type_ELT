from email.mime import base
from django.db import models
from apps.utils.models import base_model
from .category import Category
from .subcategory import SubCategory
from .topic import Topic



class QuestionBank(base_model.BaseModel):

    category = models.ForeignKey(
        Category,
        on_delete = models.PROTECT
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete = models.PROTECT
    )
    topic = models.ForeignKey(
        Topic,
        on_delete = models.PROTECT
    )
    question_data = models.JSONField(null=True)

    def __str__(self):
        return str(f"QuestionBank-{self.id}" )

    
    