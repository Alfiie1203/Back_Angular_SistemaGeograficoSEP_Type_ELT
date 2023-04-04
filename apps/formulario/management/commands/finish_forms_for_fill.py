from ...models.formulario import Formulario
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    """
        Obtiene los formularios y verifica si ya paso el dia de vencimiento para cerrarlos
    """
    help = u'Check if a form has to be closed by expiration'

    def handle(self, *args, **options):
        today = date.today()
        yesterday = today - relativedelta(days=1)
        formularios_vencidos = Formulario.objects.filter(expiration_date__lte=yesterday, status_form='ACTIVE')

        for formulario in formularios_vencidos:
            formulario.status_form = 'CLOSED'
            formulario.save()