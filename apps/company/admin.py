from django.contrib import admin
from .models import actor_type, commodity, company_group, company


class ActorTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name_es', 'proforest_actortype_code', 'commodity']
admin.site.register(actor_type.ActorType, ActorTypeAdmin)


class CommodityAdmin(admin.ModelAdmin):
    list_display = [ 'pk', 'proforest_commodity_code', 'name_es']
admin.site.register(commodity.Commodity, CommodityAdmin)


class CompanyGroupAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
admin.site.register(company_group.CompanyGroup, CompanyGroupAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'commodity', 'actor_type', 'has_superuser', 'has_responsable']
admin.site.register(company.Company, CompanyAdmin)

class ProforestCodeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
admin.site.register(company.ProforestCode, ProforestCodeAdmin)

class CompanyUserFormKeyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company', 'email']
admin.site.register(company.CompanyUserFormKey, CompanyUserFormKeyAdmin)

class ValidateCompanyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company', 'date_validation']
admin.site.register(company.ValidateCompany, ValidateCompanyAdmin)

class VerifyCompanyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company', 'date_verification']
admin.site.register(company.VerifyCompany, VerifyCompanyAdmin)


#modelos de directorios

class QuestionDriveCategoryFolderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company', 'category', 'drive_folder_category_id']
admin.site.register(company.QuestionDriveCategoryFolder, QuestionDriveCategoryFolderAdmin)

class QuestionDriveSubCategoryFolderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'company', 'category', 'subcategory','drive_folder_subcategory_id']
admin.site.register(company.QuestionDriveSubCategoryFolder, QuestionDriveSubCategoryFolderAdmin)

