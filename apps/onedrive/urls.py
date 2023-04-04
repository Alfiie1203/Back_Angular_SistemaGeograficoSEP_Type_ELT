from django.urls import path
from . import views

    # ========================  OAuth  Backoffice Landings ===============================

urlpatterns = [

    path('obtain/', views.landing_view, name = 'oauth2-landing'),
    path('token/', views.ReturnTokenView.as_view()),

]