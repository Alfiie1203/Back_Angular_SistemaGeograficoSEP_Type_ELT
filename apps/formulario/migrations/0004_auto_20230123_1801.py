# Generated by Django 3.2.15 on 2023-01-23 23:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('formulario', '0003_validateformulario_verifyformulario'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='validateformulario',
            options={'permissions': [('assign_validation_formulario', 'Can assign validation formulario')]},
        ),
        migrations.AlterModelOptions(
            name='verifyformulario',
            options={'permissions': [('assign_verification_formulario', 'Can assign verification formulario')]},
        ),
    ]
