from django.db import models
from apps.utils.models import base_model
from apps.user.models import User
from .question import Question

class RevisionControl(base_model.BaseModel):
    question = models.ForeignKey(
        Question,
        on_delete = models.PROTECT,
    )
    reviewed_by = models.ForeignKey(User,on_delete = models.PROTECT, blank=True, null=True)
    reviewer_observations =  models.TextField(blank=True, null=True)
    reviewed_answer = models.JSONField(null=True)

