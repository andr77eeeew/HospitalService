from django.urls import path

from medicalBook import views

urlpatterns = [
    path('create/', views.CreateMedicalBookView.as_view()),
    path('get/', views.GetMedicalBookView.as_view()),
]
