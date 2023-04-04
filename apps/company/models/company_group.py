from django.db import models
from apps.utils.models import base_model

class CompanyGroup(base_model.BaseModel):
    name = models.CharField(max_length = 126, unique = True)

    def __str__(self):
        return str(self.name)
