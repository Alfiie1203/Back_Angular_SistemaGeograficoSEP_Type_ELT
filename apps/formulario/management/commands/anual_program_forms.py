from django.core.management.base import BaseCommand
import logging
from apps.proforestform.models.proforestform import ProforestForm
from ...models.formulario import Formulario, Period
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
import math
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
        Obtiene los formularios y verifica si por periodicidad deben Crearse
        debe ejecutarse el primero de cada doce meses
    """
    help = u'Check if a form has to be CREATED'

    def handle(self, *args, **options):
        today = datetime.now()
        period_model = Period.objects.get(code='AN') #obtain model of period
        last_form = today - relativedelta(months=period_model.months)
        proforestforms = ProforestForm.objects.filter(period= period_model, status=True)
        open_date_year = last_form.year
        open_date_month = last_form.month
        
        for proforestform in proforestforms:
            period_code = proforestform.period.code
            period_months = proforestform.period.months
            periodo = math.ceil(open_date_month/period_months)
            period_code = period_code+'-'+str(periodo)+'-'+str(open_date_year)
            formularios = Formulario.objects.filter(proforestform=proforestform, period_code=period_code, active_next_period = True)
            for formulario in formularios:
                opendate = today.date()
                expirationdate = opendate + timedelta(formulario.validity_period)
                if formulario.end_date_validation != None:
                    deadline = formulario.end_date_validation + relativedelta(months=1)
                else:
                    deadline=None
                new_form = Formulario.objects.create(
                    proforestform  = formulario.proforestform,
                    code_form = formulario.code_form,
                    name = formulario.name,
                    created_by = formulario.created_by,
                    validity_period = formulario.validity_period,
                    period = formulario.period,
                    allocating_company = formulario.allocating_company,
                    assigned_company = formulario.assigned_company,
                    end_date_validation = deadline,
                    send_to_company_suply_base = formulario.send_to_company_suply_base,
                    status_form = 'ACTIVE', #ACTIVADO PERO DEPENDE DEL SUPERUSUARIO DARLE VISIBILIDAD?
                    open_date = opendate,
                    expiration_date = expirationdate,
                )
                new_form.revisor.set(formulario.revisor.all())
                new_form.bank_questions.set(formulario.proforestform.bank_questions.all())
                new_form.assigned_form_email()
                time.sleep(10) #Prevent exced maximun email sended in a time



        

