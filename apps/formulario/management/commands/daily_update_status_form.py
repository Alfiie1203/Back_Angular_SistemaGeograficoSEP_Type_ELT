from django.core.management.base import BaseCommand
import logging
from ...models.formulario import Formulario
from datetime import date


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
        Obtiene los formularios y verifica si por fecha se pueden pasar a activos
    """
    help = u'Check if a form has to be Visible by open date'

    def handle(self, *args, **options):
        today = date.today()

        formularios = Formulario.objects.filter(open_date__lte=today, status_form='NOTVISIBLE')
        for formulario in formularios:
            formulario.status_form = 'ACTIVE'
            formulario.save()

        
