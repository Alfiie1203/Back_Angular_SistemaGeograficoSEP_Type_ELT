# Generated by Django 3.2.15 on 2023-01-19 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_form', models.CharField(max_length=126)),
                ('name', models.CharField(max_length=126)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('open_date', models.DateField()),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('validity_period', models.IntegerField()),
                ('revision_status', models.CharField(choices=[('CHECK', 'Checked'), ('INPROCESS', 'in process'), ('WITHOUTCHECK', 'Without checking')], default='WITHOUTCHECK', max_length=16)),
                ('status_form', models.CharField(choices=[('NOTVISIBLE', 'Not visible form'), ('ACTIVE', 'Active Form'), ('CLOSED', 'Closed Form')], default='NOTVISIBLE', max_length=16)),
                ('days_of_revision', models.IntegerField(blank=True, null=True)),
                ('deadline_revision', models.DateField(blank=True, null=True)),
                ('send_to_company_suply_base', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
                ('period_code', models.CharField(blank=True, max_length=126, null=True)),
            ],
            options={
                'ordering': ['id'],
                'permissions': [('fill_out_forms', 'Can fill formulario'), ('assign_forms', 'Can asign formulario')],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('reviewer_observations', models.TextField(blank=True, null=True)),
                ('validation', models.CharField(choices=[('ARE', 'Autoreported answer'), ('VAL', 'Validated answer'), ('NVA', 'Not validated answer'), ('VER', 'Verified answer'), ('NVE', 'Not Verified answer')], default='NVA', max_length=3)),
                ('question_data', models.JSONField(blank=True, null=True)),
                ('group', models.CharField(max_length=16)),
                ('answer', models.JSONField(blank=True, null=True)),
                ('required', models.BooleanField(default=False)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('validation', models.CharField(choices=[('ARE', 'Autoreported answer'), ('VAL', 'Validated answer'), ('NVA', 'Not validated answer'), ('VER', 'Verified answer'), ('NVE', 'Not Verified answer')], max_length=3)),
                ('reviewer_observations', models.TextField(blank=True, null=True)),
                ('answer', models.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
