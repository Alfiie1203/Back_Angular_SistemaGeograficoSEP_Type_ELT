# Generated by Django 3.2.15 on 2023-01-19 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('traceability', '0001_initial'),
        ('cities_light', '0011_alter_city_country_alter_city_region_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifytraceability',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='verifytraceability',
            name='traceability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traceability.traceability'),
        ),
        migrations.AddField(
            model_name='validatetraceability',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='validatetraceability',
            name='traceability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='traceability.traceability'),
        ),
        migrations.AddField(
            model_name='traceabilityfile',
            name='reporting_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_file', to='company.company'),
        ),
        migrations.AddField(
            model_name='traceabilityfile',
            name='upload_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reporting_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='traceability',
            name='actor_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company.actortype'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cities_light.subregion'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='commodity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='company.commodity'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='company_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='company.companygroup'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cities_light.country'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cities_light.region'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='reported_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reported_company', to='company.company'),
        ),
        migrations.AddField(
            model_name='traceability',
            name='reported_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reported_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='traceability',
            name='supplier_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='supplier_company', to='company.company'),
        ),
    ]
