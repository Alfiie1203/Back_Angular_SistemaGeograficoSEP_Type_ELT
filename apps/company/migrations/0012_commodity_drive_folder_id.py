# Generated by Django 3.2.15 on 2023-03-16 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0011_alter_company_status_revision'),
    ]

    operations = [
        migrations.AddField(
            model_name='commodity',
            name='drive_folder_id',
            field=models.CharField(blank=True, max_length=126, null=True),
        ),
    ]
