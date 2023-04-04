# Generated by Django 3.2.15 on 2023-02-13 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0008_company_has_superuser'),
        ('proforestform', '0005_rename_name_of_group_proforestform_name_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='proforestform',
            name='company_assigned',
            field=models.ManyToManyField(related_name='Company_assigned', to='company.Company'),
        ),
    ]
