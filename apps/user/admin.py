from django.contrib import admin
from apps.user.models import User, Role, PasswordReset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['pk','first_name', 'role', 'company']
    list_filter = ['role', 'groups']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['pk']
admin.site.register(Role, RoleAdmin)

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    pass