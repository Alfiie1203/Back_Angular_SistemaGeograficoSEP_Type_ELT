# Generated by Django 3.2.15 on 2023-02-03 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0006_auto_20230124_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='end_date_validation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='start_date_validation',
            field=models.DateField(blank=True, null=True),
        ),
    ]
