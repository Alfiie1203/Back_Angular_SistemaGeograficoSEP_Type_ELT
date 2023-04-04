# Generated by Django 3.2.15 on 2023-01-19 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questionsbank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=64)),
                ('months', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProforestFormCode',
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
            name='ProforestForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_form', models.CharField(blank=True, max_length=126, null=True)),
                ('name', models.CharField(max_length=126)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('open_date', models.DateField()),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('reported_period', models.DateField(blank=True, null=True)),
                ('validity_period', models.IntegerField()),
                ('group_dict', models.JSONField(blank=True, null=True)),
                ('required_dict', models.JSONField(blank=True, null=True)),
                ('exclusion_dict', models.JSONField(blank=True, null=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('status', models.BooleanField(default=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('bank_questions', models.ManyToManyField(to='questionsbank.QuestionBank')),
            ],
        ),
    ]