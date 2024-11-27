from django.urls import path

from patient import views

urlpatterns = [
    path('registration/', views.PatientRegisterView.as_view()),
    path('list/', views.PatientsList.as_view()),
]