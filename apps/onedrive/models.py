from django.db import models
from apps.utils.models import base_model

# Create your models here.
class Token(base_model.BaseModel):
    token_type = models.CharField(max_length=126)
    expires_in = models.IntegerField()
    access_token =  models.TextField()

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

