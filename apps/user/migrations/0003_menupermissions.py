# Generated by Django 3.2.15 on 2023-03-08 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'permissions': [('user_view_main', 'Can view user main menu'), ('user_view_list_users', 'Can view list of users'), ('user_create_user', 'Can create a new user'), ('user_show_my_user', 'Can view own user'), ('company_view_main', 'Can view company main menu'), ('company_view_list_companies', 'Can view list of companies'), ('company_create_company', 'Can create a new company'), ('company_delete_a_company', 'Can delete a company'), ('companygroup_view_list', 'Can view company group list'), ('commodity_view_list', 'Can view commodity list'), ('actortype_view_list', 'Can view actortype list'), ('company_validation_view_list', 'Can view company validation list'), ('company_verification_view_list', 'Can view company verification list'), ('company_list_company_validation_list', 'Can view list of company to validate'), ('company_list_company_verify_list', 'Can view list of company to verify'), ('bankquestion_view_main', 'Can view bankquestion main menu'), ('bankquestion_view_list_bankquestions', 'Can view list of bankquestion'), ('bankquestion_view_list_categories', 'Can view list of categories'), ('bankquestion_view_list_subcategories', 'Can view list of subcategories'), ('bankquestion_view_list_topics', 'Can view list of topics'), ('formularios_view_main', 'Can view formularios main menu'), ('formularios_assign_formularios_list', 'Can view formularios menu to asign'), ('formularios_assign_formularios_validator', 'Can view formularios menu to asign validator'), ('formularios_assign_formularios_verificator', 'Can view formularios menu to asign verificator'), ('formularios_view_results_list', 'Can view formularios results'), ('formularios_list_formularios_to_validate', 'Can view formularios list to validate'), ('formularios_list_formularios_to_verify', 'Can view formularios list to verify'), ('supplybase_view_main', 'Can view supplybase main menu'), ('supplybase_view_list', 'Can view supplybase list'), ('supplybase_assign_supplybase_validator', 'Can view supplybase menu to asign validator'), ('supplybase_assign_supplybase_verificator', 'Can view supplybase menu to asign verificator'), ('supplybase_view_supplybase_resume_list', 'Can view resume of supplybase results'), ('supplybase_list_supplybase_to_validate', 'Can view supplybase list to validate'), ('supplybase_list_supplybase_to_verify', 'Can view supplybase list to verify')],
            },
        ),
    ]
