# Generated by Django 3.2.15 on 2023-01-30 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proforestform', '0003_proforestform_exclusion_logic_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='proforestform',
            name='name_of_group',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
