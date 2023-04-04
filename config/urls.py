from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import  include, path

from apps.dashboard import urls as dashboard_urls
from apps.company import urls as company_urls
from apps.coordinates import urls as coordinates_urls
from apps.formulario import urls as formulario_urls
from apps.proforestform import urls as proforestform_urls
from apps.questionsbank import urls as questionbank_urls
from apps.traceability import urls as traceability_urls
from apps.supplybase import urls as supplybase_urls
from apps.user import urls as user_urls
from apps.onedrive import urls as onedrive_urls
from apps.emailcustom import urls as emailcustom_urls


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    #admin de Django
    path('adminproforest/', admin.site.urls), 


    #Include Auth urls
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #Include dashboard app
    path('', include(dashboard_urls)),

    #Include Urls of Company APP
    path('company/', include(company_urls)),

    #Include Urls of Question Bank
    path('questionbank/', include (questionbank_urls)),

    #Include Urls of ProforestForm
    path('proforestform/', include (proforestform_urls)),

    #Include Urls of Formularios
    path('formulario/', include (formulario_urls)),
    #Include Traceability URLS

    path('traceability/', include (traceability_urls)),

    #Include User custom Urls
    path('users/', include(user_urls)),

    #Include Cities app Urls
    path('cities/', include('apps.cities.urls')),

    #Coordinates Validate Views
    path('coordinates/', include(coordinates_urls)),

    #Dependency Supply Base
    path('supplybase/', include(supplybase_urls)),

    #Email Template Views
    path('email/', include(emailcustom_urls)),

    #Landing for onedrive Oauth2
    path('onedrive/', include(onedrive_urls)),


    #Generic auth Views
    path('auth/login/',  auth_views.LoginView.as_view( template_name='adminlte/base/login.html' ), name='login'),
    path('auth/logout/', auth_views.logout_then_login, name='logout'),

    #HelperView to change Language
    path('i18n/', include('django.conf.urls.i18n'))

]
