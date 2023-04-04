import yaml
import msal
import requests
from ...models import Token
import os
from django.core.management.base import BaseCommand, CommandError


file_path = os.path.join(os.path.dirname(__file__), 'oauthsettings.yml')

class Command(BaseCommand):

    help = u'Go to Microsoft sharepoint autenticate obtain and save token'

    def handle(self, *args, **options):

        # Load the oauth_settings.yml file located in your app DIR
        with open(file_path, 'r') as f:
            settings = yaml.safe_load(f)
            id_directorio_inquilino = settings['id_directorio_inquilino']
            client_id = settings['client_id']
            id_directorio_inquilino = settings['id_directorio_inquilino']

            scope = settings['scope']
            client_secret = settings['client_secret']
            authority = f'https://login.microsoftonline.com/{id_directorio_inquilino}'
            
            app = msal.ConfidentialClientApplication(
                client_id=client_id,
                client_credential=client_secret,
                authority=authority
            )

            result = app.acquire_token_for_client(scopes=scope)

            token = Token.objects.create(
            token_type = result['token_type'],
            expires_in = result['expires_in'],
            access_token = result['access_token'],
            )
            return 


