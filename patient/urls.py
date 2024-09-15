from django.urls import path

from patient import views

urlpatterns = [
    path('list/', views.PatientsList.as_view()),
    path('create-appointment/', views.CreateAppointmentView.as_view()),
]