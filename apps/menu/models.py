from django.db import models

# Create your models here.
class MenuPermissions(models.Model):
    name = models.CharField(max_length=128)
    
    class Meta:
        permissions =[
            ("user_view_main", "Menu Can view user main menu"),
            ("user_view_list_users", "Menu Can view list of users"),
            ("user_create_user", "Menu Can create a new user"),
            ("user_show_my_user", "Menu Can view own user"),

            ("company_view_main", "Menu Can view company main menu"),
            ("company_view_list_companies", "Menu Can view list of companies"),
            ("company_create_company", "Menu Can create a new company"),
            ("company_delete_a_company", "Menu Can delete a company"),
            ("companygroup_view_list", "Menu Can view company group list"),
            ("commodity_view_list", "Menu Can view commodity list"),
            ("actortype_view_list", "Menu Can view actortype list"),
            ("company_assign_validator_list", "Menu Can asign company validator"),
            ("company_assign_verificator_list", "Menu Can asign company verificator"),
            ("company_list_validation_list", "Menu Can view list of company to validate"),
            ("company_list_verification_list", "Menu Can view list of company to verify"),

            ("bankquestion_view_main", "Menu Can view bankquestion main menu"),
            ("bankquestion_view_list_bankquestions", "Menu Can view list of bankquestion"),
            ("bankquestion_view_list_categories", "Menu Can view list of categories"),
            ("bankquestion_view_list_subcategories", "Menu Can view list of subcategories"),
            ("bankquestion_view_list_topics", "Menu Can view list of topics"),

            ("formularios_view_main", "Menu Can view formularios main menu"),
            ("formularios_view_list_formularios", "Menu Can view list of formularios"),
            ("formularios_assign_formularios_list", "Menu Can view formularios menu to asign"),
            ("formularios_assign_formularios_validator", "Menu Can view formularios menu to asign validator"),
            ("formularios_assign_formularios_verificator", "Menu Can view formularios menu to asign verificator"),
            ("formularios_view_results_list", "Menu Can view formularios results"),
            ("formularios_list_formularios_to_validate", "Menu Can view formularios list to validate"),
            ("formularios_list_formularios_to_verify", "Menu Can view formularios list to verify"),

            ("supplybase_view_main", "Menu Can view supplybase main menu"),
            ("supplybase_view_list", "Menu Can view supplybase list"),
            ("supplybase_assign_supplybase_validator", "Menu Can view supplybase menu to asign validator"),
            ("supplybase_assign_supplybase_verificator", "Menu Can view supplybase menu to asign verificator"),
            ("supplybase_view_supplybase_resume_list", "Menu Can view resume of supplybase results"),
            ("supplybase_list_supplybase_to_validate", "Menu Can view supplybase list to validate"),
            ("supplybase_list_supplybase_to_verify", "Menu Can view supplybase list to verify"),

        ]

        