# Generated by Django 3.2.15 on 2023-02-22 21:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('traceability', '0006_auto_20230126_1341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='traceability',
            name='validator_user',
        ),
        migrations.AddField(
            model_name='traceability',
            name='validator_user',
            field=models.ManyToManyField(blank=True, related_name='validator_traceability', to=settings.AUTH_USER_MODEL),
        ),
    ]
