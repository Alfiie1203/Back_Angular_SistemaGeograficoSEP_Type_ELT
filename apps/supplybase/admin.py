from django.contrib import admin
from .models import supplybase

# Register your models here.
class SupplyBaseAdmin(admin.ModelAdmin):
    list_display = ["pk", "company", "supplier_company"]
admin.site.register(supplybase.SupplyBase, SupplyBaseAdmin)

class SupplyBaseDependencyAdmin(admin.ModelAdmin):
    list_display = ["pk", "actor_type" ]
admin.site.register(supplybase.SupplyBaseDependency, SupplyBaseDependencyAdmin)

class SupplyBaseRegisterAdmin(admin.ModelAdmin):
    list_display = ["pk", "company", "register_year", "period", "purchased_volume"]
admin.site.register(supplybase.SupplyBaseRegister, SupplyBaseRegisterAdmin)

class PurchasedPercentageAdmin(admin.ModelAdmin):
    list_display = ["pk", "supplybase_register", "percentage", "actor_type"]
admin.site.register(supplybase.PurchasedPercentage, PurchasedPercentageAdmin)
