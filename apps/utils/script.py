#===========================================
# paso a produccion
#===========================================

from django.contrib.auth.models import Group
from apps.user.models import Role

GRUPOS = [
    'SUPERUSUARIO', 'USUARIO'
]
new_groups = []
for grupo in GRUPOS:
    new_groups.append(Group.objects.create(
        name=grupo
        )
    )

rol = Role.objects.create(name = "CLIENTE")
rol.groups.set(new_groups)

GRUPOS = [
    'SUPERADMINISTRADOR', 'ADMINISTRADOR', 'VERIFICADOR', 'VALIDADOR',
]
new_groups = []
for grupo in GRUPOS:
    new_groups.append(Group.objects.create(
        name=grupo
        )
    )

rol = Role.objects.create(name = "COLABORADOR")
rol.groups.set(new_groups)


# from apps.company.models.company import Company
# from apps.company.models.commodity import Commodity
# from apps.company.models.actor_type import ActorType

# proforest = Company.objects.create(
#     name = 'Proforest',
#     identifier_global_company ='PROFORESTGLOBAL',
#     identifier_proforest_company ='PROFORESTGLOBAL',
#     nit = '9010278746',
    
# )

# print("creado: ", proforest)

from apps.proforestform.models.proforestform import Period

PERIODOS = [
    (1, 'MONTHLY', 'MO',),
    (2, 'BIMONTHLY', 'BM',),
    (3, 'QUARTERLY', 'QM',),
    (6, 'BIANNUAL', 'BA',),
    (12, 'ANNUAL', 'AN')
]

for period in PERIODOS:
    pe = Period.objects.create(
        code= period[2],
        name = period[1],
        months = period[0]
    )

from apps.emailcustom.models import EmailTemplate

with open('templates/mail/assigned_as_company_validator.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Asignado como validador de compañia',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'assigned_as_company_validator'
    )

with open('templates/mail/assigned_as_company_verificator.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Asignado como verificador de compañia',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'assigned_as_company_verificator'
    )

with open('templates/mail/new_form_assigned.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Nuevo formulario asignado',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'new_form_assigned'
    )

with open('templates/mail/new_user_form_assigned.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Nuevo Usuario y formulario asignado',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'new_user_form_assigned'
    )


with open('templates/mail/validate_coordinates_of_company.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido validadas las coordenadas de su Empresa',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'validate_coordinates_of_company'
    )

with open('templates/mail/validate_coordinates_of_traceability.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Informe de validacion de Trazabilidad',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'validate_coordinates_of_traceability'
    )

with open('templates/mail/verify_coordinates_of_company.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Las coordenadas de su compañia han sido Verificadas',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'verify_coordinates_of_company'
    )

with open('templates/mail/verify_coordinates_of_traceability.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido Verificada la trazabilidad de su empresa',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'verify_coordinates_of_traceability'
    )

with open('templates/mail/validate_form_resume.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido Validado el Formulario asignado a su empresa',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'validate_form_resume'
    )


with open('templates/mail/validate_info_assigned_company.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido Validado el Formulario asignado',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'validate_info_assigned_company'
    )

with open('templates/mail/verificate_form_resume.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido Verificado el Formulario asignado',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'verificate_form_resume'
    )

with open('templates/mail/verificate_info_assigned_company.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido Verificado el Formulario asignado',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'verificate_info_assigned_company'
    )

with open('templates/mail/assigned_as_traceability_validator.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido asignado como Validador de Trazabilidad',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'assigned_as_traceability_validator'
    )

with open('templates/mail/assigned_as_traceability_verificator.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido asignado como Verificador de Trazabilidad',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'assigned_as_traceability_verificator'
    )

with open('templates/mail/new_user_client_created.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido creado su Usuario en Proforest SEP',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'new_user_client_created'
    )
#pendiente cargar en produccion
with open('templates/mail/assigned_as_collaborator_in_form.html', 'r') as file:
    html_content = file.read()
    EmailTemplate.objects.create(
        subject = 'Ha sido asignado como Colaborador en un Formulario',
        from_email = 'notification@proforest.net',
        html_template = html_content,
        is_html = True,
        template_key = 'assigned_as_collaborator_in_form'
    )


#===========================================
#       creador de folders OneDrive
#===========================================
from apps.company.models.company import Company
from apps.company.models.commodity import Commodity
from apps.company.models.actor_type import ActorType



for commodity in Commodity.objects.all():
    print("revisando commodity", commodity)
    commodity.save()
    print("update commodity", commodity) #oko desactivar la otra señal cuando lo aplique

for actortype in ActorType.objects.all():
    print("revisando actortype", actortype)
    actortype.save()
    print("update actortype", actortype)


for company in Company.objects.all():
    print("revisando company", company)
    company.save()
    print("update company", company)
    
from apps.formulario.models.question import Question #crear los folders para preguntas existentes
from apps.questionsbank.models.questionbank import QuestionBank

questionsbanks = QuestionBank.objects.all()
for questionbank in questionsbanks:
    questions_forms = Question.objects.filter(question_bank = questionbank)
    for question in questions_forms:
        print("verificando el question :", question)
        question.save()
#===========================================
#       opcional solo developer
#===========================================


from apps.company.models.commodity import Commodity
from apps.company.models.actor_type import ActorType
from apps.company.models.company_group import CompanyGroup


aceite_palma = Commodity.objects.create(
    name_es = 'Aceite de Palma',
    name_en = 'Palm Oil',
    name_pt = 'Óleo de palma',
    proforest_commodity_code = 'PO',
    )

ACTOR_TYPE = [
    ('Productor Palma','PP'),
    ('Planta extractora','EP'),
    ('Refinería','RP'),
    ('Comercializadora','CP'),
]

for actortype in ACTOR_TYPE:
    actor = ActorType.objects.create(
        name_es = 'es_'+actortype[0],
        name_en = 'en_'+actortype[0],
        name_pt = 'pt_'+actortype[0],
        proforest_actortype_code = actortype[1],
        commodity = aceite_palma,
        is_productor=False
    )
    print("creado", actor)

#===========================================

cana_azucar = Commodity.objects.create(
    name_en = 'Sugar cane',
    name_es = 'Caña Azucar',
    name_pt = 'Cana de açúcar',
    proforest_commodity_code = 'SC',
    )

ACTOR_TYPE = [
    ('Productor Caña','PA'),
    ('Comercializador Caña','CA'),
    ('Refinador Caña','MZ'),
]

for actortype in ACTOR_TYPE:
    actor = ActorType.objects.create(
        name_es = 'es_'+actortype[0],
        name_en = 'en_'+actortype[0],
        name_pt = 'pt_'+actortype[0],
        proforest_actortype_code = actortype[1],
        commodity = cana_azucar
    )
    print("creado", actor)


#===========================================

soya = Commodity.objects.create(
    name_es = 'Soya',
    name_en = 'Soy',
    name_pt = 'Soja',
    proforest_commodity_code = 'SY',
    )

ACTOR_TYPE = [
    ('Productor Soya','PS'),
    ('Planta Soya','LS'),
    ('Refinería Soya','RS'),
    ('Comercializadora Soya','CS'),
]

for actortype in ACTOR_TYPE:
    actor = ActorType.objects.create(
        name_en = 'en_'+actortype[0],
        name_es = 'es_'+actortype[0],
        name_pt = 'pt_'+actortype[0],
        proforest_actortype_code = actortype[1],
        commodity = soya
    )
    print("creado", actor)


#===========================================

cafe = Commodity.objects.create(
    name_es = 'Café',
    name_en = 'Coffee',
    name_pt = 'Café',
    proforest_commodity_code = 'CF',
    )

ACTOR_TYPE = [
    ('Productor Café','CF'),
    ('Planta procesadora Café','CE'),
    ('Comercializadora Café','FC'),
    ('Café Mayorista','FM'),
    ('Café Minorista','CD'),
]

for actortype in ACTOR_TYPE:
    actor = ActorType.objects.create(
        name_es = 'es_'+actortype[0],
        name_en = 'en_'+actortype[0],
        name_pt = 'pt_'+actortype[0],
        proforest_actortype_code = actortype[1],
        commodity = cafe,
        is_productor=False

    )
    print("creado", actor)



