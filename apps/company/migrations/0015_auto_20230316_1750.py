# Generated by Django 3.2.15 on 2023-03-16 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0014_company_drive_folder_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='drive_folder_category_id',
            field=models.CharField(blank=True, max_length=126, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='drive_folder_subcategory_id',
            field=models.CharField(blank=True, max_length=126, null=True),
        ),
    ]