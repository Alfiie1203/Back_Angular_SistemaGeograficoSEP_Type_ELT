# Generated by Django 3.2.15 on 2023-01-23 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_auto_20230120_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='actortype',
            name='is_productor',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
