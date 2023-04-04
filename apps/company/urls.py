from django.urls import path
from rest_framework import routers

from .views import actor_type_views, commodity_views, company_group_views, company_views

router = routers.SimpleRouter()

urlpatterns = [
# ========================  ActorType Endpoints  ===============================
    path('actortype/list/', actor_type_views.ActorTypeList.as_view()),
    path('actortype/search/', actor_type_views.ActorTypeSearch.as_view()),
    path('actortype/create/', actor_type_views.ActorTypeCreate.as_view()),
    path('actortype/view/<int:pk>/', actor_type_views.ActorTypeView.as_view()),
    path('actortype/update/<int:pk>/',
        actor_type_views.ActorTypeUpdate.as_view()),
    path('actortype/destroy/<int:pk>/',
        actor_type_views.ActorTypeDestroy.as_view()),

# ========================  Commodity Endpoints  ===============================
    path('commodity/list/', commodity_views.CommodityList.as_view()),
    path('commodity/search/', commodity_views.CommoditySearch.as_view()),
    path('commodity/list-create-company-form/', commodity_views.CommodityListCreateCompanyForm.as_view()),
    path('commodity/create/', commodity_views.CommodityCreate.as_view()),
    path('commodity/view/<int:pk>/', commodity_views.CommodityView.as_view()),
    path('commodity/view-create-company-form/<int:pk>/', commodity_views.CommodityViewCreateCompanyForm.as_view()),
    path('commodity/update/<int:pk>/', commodity_views.CommodityUpdate.as_view()),
    path('commodity/destroy/<int:pk>/',
        commodity_views.CommodityDestroy.as_view()),

# ========================  CompanyGroup  Endpoints  ===============================
    path('companygroup/list/', company_group_views.CompanyGroupList.as_view()),
    path('companygroup/search/', company_group_views.CompanyGroupSearch.as_view()),
    path('companygroup/list-create-company-form/', company_group_views.CompanyGroupListCreateCompanyForm.as_view()),
    path('companygroup/create/', company_group_views.CompanyGroupCreate.as_view()),
    path('companygroup/view/<int:pk>/', company_group_views.CompanyGroupView.as_view()),
    path('companygroup/update/<int:pk>/', company_group_views.CompanyGroupUpdate.as_view()),
    path('companygroup/destroy/<int:pk>/', company_group_views.CompanyGroupDestroy.as_view()),

# ========================  Company Endpoints  ===============================
    path('company/list/', company_views.CompanyList.as_view()),
    path('company/search/', company_views.CompanySearch.as_view()),
    path('company/list-create-user-form/', company_views.CompanyListCreateUserForm.as_view()),
    path('company/create/', company_views.CompanyCreate.as_view()),
    path('company/previousproforestcode/', company_views.PreviousProforestCode.as_view()),
    path('company/view/<int:pk>/', company_views.CompanyView.as_view()),
    path('company/update/<int:pk>/', company_views.CompanyUpdate.as_view()),
    path('company/destroy/<int:pk>/', company_views.CompanyDestroy.as_view()),
    path('deletebycode/', company_views.CompanyDelete.as_view()),
    path('company/search/detail/', company_views.CompanySearchDetail.as_view()),
    path('company/search/plantillaxlsx/', company_views.CompanySearchPlantillaXlsx.as_view()),




# ============================= Templates Views Company ============================
    path('viewlist/', company_views.CompanyListView.as_view(),
        name=company_views.CompanyListView.url_name),

    path('viewcreate/', company_views.CompanyCreateView.as_view(),
        name=company_views.CompanyCreateView.url_name),

    path('company/viewupdate/<int:pk>/',  company_views.CompanyUpdateView.as_view(),
        name=company_views.CompanyUpdateView.url_name),

    path('company/viewdeactivate/', company_views.CompanyDeactivateView.as_view(),
        name=company_views.CompanyDeactivateView.url_name),

    path('company/viewdelete/', company_views.CompanyDeleteView.as_view(),
        name=company_views.CompanyDeleteView.url_name),

    path('company/viewlist/export/', company_views.CompanyExportView.as_view(),
        name=company_views.CompanyExportView.url_name),
    # =============================================================================

    # ============================= Templates Views Commodity ============================
    path('commodity/viewlist/', commodity_views.CommodityListView.as_view(),
        name=commodity_views.CommodityListView.url_name),
    path('commodity/viewcreate/', commodity_views.CommodityCreateView.as_view(),
        name=commodity_views.CommodityCreateView.url_name),

    path('commodity/viewupdate/<int:pk>/',  commodity_views.CommodityUpdateView.as_view(),
        name=commodity_views.CommodityUpdateView.url_name),

    path('commodity/deactivate/', commodity_views.CommodityDeactivateView.as_view(),
        name=commodity_views.CommodityDeactivateView.url_name),

    path('commodity/delete/', commodity_views.CommodityDeleteView.as_view(),
        name=commodity_views.CommodityDeleteView.url_name),

    path('commodity/list/export/', commodity_views.CommodityExportView.as_view(),
        name=commodity_views.CommodityExportView.url_name),
    # =============================================================================

    # ============================= Templates Views Actor Type ============================
    path('actor-type/viewlist/', actor_type_views.ActorTypeListView.as_view(),
        name=actor_type_views.ActorTypeListView.url_name),

    path('actor-type/viewcreate/', actor_type_views.ActorTypeCreateView.as_view(),
        name=actor_type_views.ActorTypeCreateView.url_name),

    path('actor-type/viewupdate/<int:pk>/',  actor_type_views.ActorTypeUpdateView.as_view(),
        name=actor_type_views.ActorTypeUpdateView.url_name),

    path('actor-type/deactivate/', actor_type_views.ActorTypeDeactivateView.as_view(),
        name=actor_type_views.ActorTypeDeactivateView.url_name),

    path('actor-type/delete/', actor_type_views.ActorTypeDeleteView.as_view(),
        name=actor_type_views.ActorTypeDeleteView.url_name),

    path('actor-type/list/export/', actor_type_views.ActorTypeExportView.as_view(),
        name=actor_type_views.ActorTypeExportView.url_name),
    
    path('actor-type/commodity/<int:id_commodity>/list/', actor_type_views.ActorTypeCommodityList.as_view(),
        name='actortype-commodity-list'),
    # =============================================================================
]
