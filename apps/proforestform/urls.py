from django.urls import path
from .views import proforestform_views, period_views

urlpatterns = [
    path('list/', proforestform_views.ProforestFormList.as_view()),
    path('create/', proforestform_views.ProforestFormCreate.as_view()),
    path('view/<int:pk>/', proforestform_views.ProforestFormView.as_view()),
    path('update/<int:pk>/', proforestform_views.ProforestFormUpdate.as_view()),
    path('destroy/<int:pk>/', proforestform_views.ProforestFormDestroy.as_view()),
    path('list_questions/<int:pk>/', proforestform_views.ProforestFormDetail.as_view()),

    path('periodlist/', period_views.PeriodList.as_view()),
    path('previouscode/', proforestform_views.GetPreviouscode.as_view()),



]

