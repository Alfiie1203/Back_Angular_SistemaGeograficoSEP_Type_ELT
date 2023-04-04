from django.db import models
from apps.utils.models import base_model
from .commodity import Commodity
from django.dispatch import receiver
from django.db.models.signals import post_save
import requests
import json




class ActorType(base_model.BaseModel):
    name_es = models.CharField(max_length = 126, unique = True)
    name_en = models.CharField(max_length = 126, unique = True)
    name_pt = models.CharField(max_length = 126, unique = True)
    is_productor = models.BooleanField()
    proforest_actortype_code = models.CharField(max_length = 2, unique = True)
    commodity = models.ForeignKey(
        Commodity,
        related_name='actor_type',
        on_delete = models.PROTECT
    )
    drive_folder_id = models.CharField(max_length = 126, blank=True, null=True)

    def __str__(self):
        return str(self.name_es)
    

@receiver(post_save, sender=ActorType)
def create_folder_onedrive(sender, instance, **kwargs):
    from apps.onedrive.models import Token
    # instance = kwargs.get('instance')
    if (instance.drive_folder_id == None or instance.drive_folder_id == ''):
        
        drive_commodity = instance.commodity.drive_folder_id
        URL_ONEDRIVE = f'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/items/{drive_commodity}/children'
       
        token = Token.objects.latest()
        data = {
            "name": f'{instance.name_es.strip()}',
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