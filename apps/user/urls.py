from django.urls import  path
from rest_framework import routers

from .views.user_views import ( MeApiView, UserCreateApiView, UserListApiView, UserDetailApiView,
                PasswordResetView, PasswordResetDoneView, UserUpdateApiView, ListCollaboratorsApi )

from .views.user_views import (UserListView, UserAddView, UserDetailView, UserUpdateView, UserListExportView)
from .views.user_views import (UserDeleteView, UserDeactivateView, UserDestroy)

from .views.roles_views import RoleListView, RoleAddView, RoleDetailView, RoleUpdateView, RoleDeleteView

from .views.subrole_views import (SubroleListView, SubroleCreateView, SubroleDetailView, SubroleUpdateView)

from .views.roles_views import RoleApiListView

from .views.subrole_views import SubRoleApiListView, SubRolePermissionsApiListView


router = routers.SimpleRouter()

# router.register('', UserViewSet, basename='urls_user')


urlpatterns = [
    # ========================  Api User Endpoints  ===============================
    path('me/', MeApiView.as_view()),
    path('list/', UserListApiView.as_view()),
    path('create/', UserCreateApiView.as_view()),
    path('view/<int:pk>/', UserDetailApiView.as_view()),
    path('update/<int:pk>/', UserUpdateApiView.as_view()),
    path('password/reset/', PasswordResetView.as_view()),
    path('password/reset/done/<slug:slug>/', PasswordResetDoneView.as_view()),
    path('delete/', UserDeleteView.as_view(), name=UserDeleteView.url_name),
    path('deactivate/', UserDeactivateView.as_view(), name=UserDeactivateView.url_name),
    path('destroy-api/<int:pk>/', UserDestroy.as_view()),
    path('collaborators/', ListCollaboratorsApi.as_view()),


    # ============================= Templates Views User =================================
    path('viewlist/', UserListView.as_view(), name=UserListView.url_name),
    path('list/export/', UserListExportView.as_view(), name=UserListExportView.url_name),
    path('viewcreate/', UserAddView.as_view(), name=UserAddView.url_name),
    path('view/<int:pk>/detail/', UserDetailView.as_view(), name=UserDetailView.url_name),
    path('view/<int:pk>/update/', UserUpdateView.as_view(), name=UserUpdateView.url_name),

    # ============================= Templates Views Role =================================
    path('role/list/', RoleListView.as_view(), name=RoleListView.url_name),
    path('role/create/', RoleAddView.as_view(), name=RoleAddView.url_name),
    path('role/<int:pk>/detail/', RoleDetailView.as_view(), name=RoleDetailView.url_name),
    path('role/<int:pk>/update/', RoleUpdateView.as_view(), name=RoleUpdateView.url_name),
    path('role/delete/', RoleDeleteView.as_view(), name=RoleDeleteView.url_name),


    # ============================= Templates Views SubRole extends from GROUP ===========
    path('subrole/list/', SubroleListView.as_view(), name=SubroleListView.url_name),
    path('subrole/create/', SubroleCreateView.as_view(), name=SubroleCreateView.url_name),
    path('subrole/<int:pk>/detail/', SubroleDetailView.as_view(), name=SubroleDetailView.url_name),
    path('subrole/<int:pk>/update/', SubroleUpdateView.as_view(), name=SubroleUpdateView.url_name),
    
    # ============================= API Views SubRole  ==================================
    path('role/api/list/', RoleApiListView.as_view(), name="role-apilist"),
    path('subrole/api/list/<int:role_id>/', SubRoleApiListView.as_view(), name="subrole-apilist"), #BACKOFFICE
    path('subrole/permissions/api/list/<int:pk>/', SubRolePermissionsApiListView.as_view(), name="subrole-permissions-apilist"), #BACKOFFICE


]

urlpatterns += router.urls