from django.contrib import admin
from .models import Token
# Register your models here.

class TokenAdmin(admin.ModelAdmin):
    list_display = ['id']

admin.site.register(Token, TokenAdmin)