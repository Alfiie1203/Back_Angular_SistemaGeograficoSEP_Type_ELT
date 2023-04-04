from django.urls import path
from .views import backoffice_views, supplybase_views

urlpatterns = [
    # ========================  SupplyBase Backoffice  ===============================

    path('list/', backoffice_views.SupplybasedependencyList.as_view(),
        name=backoffice_views.SupplybasedependencyList.url_name),
    path('create/', backoffice_views.SupplybasedependencyCreate.as_view(),
        name=backoffice_views.SupplybasedependencyCreate.url_name),
    path('update/<int:pk>/', backoffice_views.SupplybasedependencyUpdate.as_view(),
        name=backoffice_views.SupplybasedependencyUpdate.url_name),
    
    # ========================  SuppliBase Endpoints  ===============================

    path('api/list/', supplybase_views.SupplyBaseRegisterList.as_view()),
    path('api/getdependencies/', supplybase_views.SupplyBaseGetDependency.as_view()),
    path('api/checkregister/', supplybase_views.CheckSupplyBaseRegister.as_view()),
    path('api/create/', supplybase_views.SupplyBaseCreate.as_view()),
    path('api/detail/<int:pk>/', supplybase_views.SupplyBaseDetailView.as_view()),

    path('api/obtainsupplybase/location/', supplybase_views.ObtainSupplyBaseRegistersLocation.as_view()),
    path('api/detail/compareview/<int:pk>/', supplybase_views.SupplyBaseTotalResumeView.as_view()),
    path('api/update/purchasedpercentage/<int:pk>/', supplybase_views.PurchasedPercentageUpdateView.as_view()),


]