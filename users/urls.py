from django.urls import path

from users import views

urlpatterns = [
    path('patient-registration/', views.PatientRegisterView.as_view(), name='patient-registration'),
]