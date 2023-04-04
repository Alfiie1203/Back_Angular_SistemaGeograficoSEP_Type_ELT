from django.urls import path
from .views import category_views
from .views import subcategory_views
from .views import topic_views
from .views import questionbank_views
from .views import presave_questionbank_views



urlpatterns = [
    path('category/list/', category_views.CategoryList.as_view()),
    path('category/search/', category_views.CategorySearch.as_view()),
    path('category/create/', category_views.CategoryCreate.as_view()),
    path('category/view/<int:pk>/', category_views.CategoryView.as_view()),
    path('category/update/<int:pk>/', category_views.CategoryUpdate.as_view()),
    path('category/destroy/<int:pk>/', category_views.CategoryDestroy.as_view()),

    path('subcategory/list/', subcategory_views.SubCategoryList.as_view()),
    path('subcategory/search/', subcategory_views.SubCategorySearch.as_view()),
    path('subcategory/create/', subcategory_views.SubCategoryCreate.as_view()),
    path('subcategory/view/<int:pk>/', subcategory_views.SubCategoryView.as_view()),
    path('subcategory/update/<int:pk>/', subcategory_views.SubCategoryUpdate.as_view()),
    path('subcategory/destroy/<int:pk>/', subcategory_views.SubCategoryDestroy.as_view()),

    path('topic/list/', topic_views.TopicList.as_view()),
    path('topic/list/simple/', topic_views.TopicListSimple.as_view()),
    path('topic/search/', topic_views.TopicSearch.as_view()),
    path('topic/create/', topic_views.TopicCreate.as_view()),
    path('topic/view/<int:pk>/', topic_views.TopicView.as_view()),
    path('topic/update/<int:pk>/', topic_views.TopicUpdate.as_view()),
    path('topic/destroy/<int:pk>/', topic_views.TopicDestroy.as_view()),

    path('list/', questionbank_views.QuestionBankList.as_view()),
    path('create/', questionbank_views.QuestionBankCreate.as_view()),
    path('view/<int:pk>/', questionbank_views.QuestionBankView.as_view()),
    path('update/<int:pk>/', questionbank_views.QuestionBankUpdate.as_view()),
    path('destroy/<int:pk>/', questionbank_views.QuestionBankDestroy.as_view()),

    #temporal template test javascript
    path('javascript/', questionbank_views.JavascriptView.as_view()),
    path('detail/temp/view/', questionbank_views.django_models_json,
            name='question-detail'),

    #Prueba de guardado temporal
    path('presave/', presave_questionbank_views.QuestionSave.as_view() ),

]
