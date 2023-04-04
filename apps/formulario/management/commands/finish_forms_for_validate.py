from ...models.formulario import Formulario
from datetime import datetime
from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    """
        Obtiene los formularios en proceso de validacion y valida si paso el dia de vencimiento para cerrarlos
    """
    help = u'Check if a form has to be closed his validation time'

    def handle(self, *args, **options):
        today = date.today()
        yesterday = today - relativedelta(days=1)
        formularios_vencidos = Formulario.objects.filter(end_date_validation__lte=today, revision_status = 'INVALIDATINGPROCESS')

        for formulario in formularios_vencidos:
            formulario.revision_status = 'VALIDATE'
            formulario.save()