# Generated by Django 3.2.15 on 2023-01-19 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActorType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('name_es', models.CharField(max_length=126, unique=True)),
                ('name_en', models.CharField(max_length=126, unique=True)),
                ('name_pt', models.CharField(max_length=126, unique=True)),
                ('proforest_actortype_code', models.CharField(max_length=2, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('name_es', models.CharField(max_length=126, unique=True)),
                ('name_en', models.CharField(max_length=126, unique=True)),
                ('name_pt', models.CharField(max_length=126, unique=True)),
                ('proforest_commodity_code', models.CharField(max_length=2, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=126)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('identifier_global_company', models.CharField(blank=True, max_length=126, null=True, unique=True)),
                ('identifier_proforest_company', models.CharField(blank=True, max_length=126, null=True, unique=True)),
                ('nit', models.CharField(max_length=126)),
                ('has_responsable', models.BooleanField(default=False)),
                ('company_profile', models.CharField(blank=True, choices=[('SC', 'Suplier Client'), ('PC', 'Proforest Client'), ('SO', 'Suplier Client Other')], max_length=2)),
                ('deadline_validation', models.DateField(blank=True, null=True)),
                ('status_revision', models.CharField(blank=True, choices=[('SR', 'Self Reported'), ('NV', 'Not Validated'), ('VA', 'Validated'), ('NVE', 'Not Verified'), ('VE', 'Verified')], max_length=3, null=True)),
                ('note_revision', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
                'permissions': [('update_own_company', 'Can Update his own Company')],
            },
        ),
        migrations.CreateModel(
            name='CompanyGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=126, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanyUserFormKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('email', models.EmailField(max_length=254)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProforestCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=126, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ValidateCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_validation', models.DateTimeField(auto_now_add=True)),
                ('status_revision', models.CharField(max_length=3)),
            ],
            options={
                'permissions': [('assign_validation_company', 'Can Assign Validation Company')],
            },
        ),
        migrations.CreateModel(
            name='VerifyCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_verification', models.DateTimeField(auto_now_add=True)),
                ('status_revision', models.CharField(max_length=3)),
            ],
            options={
                'permissions': [('assign_verification_company', 'Can Assign Validation Company')],
            },
        ),
    ]
