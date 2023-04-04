from django.urls import path
from .views import backoffice_views


urlpatterns = [
    # ========================  SupplyBase Backoffice  ===============================

    path('list/', backoffice_views.EmailTemplateList.as_view(),
        name=backoffice_views.EmailTemplateList.url_name),
    # path('create/', backoffice_views.EmailCustomCreate.as_view(),
    #     name=backoffice_views.EmailCustomCreate.url_name),
    path('update/<int:pk>/', backoffice_views.EmailTemplateUpdate.as_view(),
        name=backoffice_views.EmailTemplateUpdate.url_name),
]