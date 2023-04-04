from django.db import models
from apps.utils.models import base_model
from django.dispatch import receiver
from django.db.models.signals import post_save
import requests
import json

from config.settings import URL_ONEDRIVE

class Commodity(base_model.BaseModel):
    name_es = models.CharField(max_length = 126, unique = True)
    name_en = models.CharField(max_length = 126, unique = True)
    name_pt = models.CharField(max_length = 126, unique = True)
    proforest_commodity_code = models.CharField(max_length = 2, unique = True)
    drive_folder_id = models.CharField(max_length = 126, blank=True, null=True)
    def __str__(self):
        return str(self.name_es)

@receiver(post_save, sender=Commodity)
def update_actor_of_commodity_status(sender, instance, **kwargs):
    from apps.company.models.actor_type import ActorType #avoid circular importation
    
    actors = ActorType.objects.filter(commodity=instance)
    for actor in actors:
        actor.status = instance.status
        actor.save()
    return



@receiver(post_save, sender=Commodity)
def create_folder_onedrive(sender, **kwargs):
    from apps.onedrive.models import Token
    instance = kwargs.get('instance')
    if (instance.drive_folder_id == None or instance.drive_folder_id == ''):
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