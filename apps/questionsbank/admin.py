from django.contrib import admin
from .models.category import Category
from .models.questionbank import QuestionBank
from .models.subcategory import SubCategory
from .models.topic import Topic


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_es', 'name_pt', 'code', 'status']

admin.site.register(Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = [ 'name_en', 'name_es', 'name_pt', 'category', 'code', 'status' ]

admin.site.register(SubCategory, SubCategoryAdmin)

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_es', 'name_pt', 'subcategory', 'code', 'status']

admin.site.register(Topic, TopicAdmin)

class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['pk', 'category', 'subcategory', 'topic', 'status']

admin.site.register(QuestionBank, QuestionBankAdmin)
