from django.urls import path
from doctor import views

urlpatterns = [
    path('registration/', views.DoctorRegisterView.as_view()),
    path('key-validate/', views.DoctorKeyValidatorView.as_view()),
    path('update/', views.DoctorUpdateView.as_view()),
    path('specialist/', views.SpecialistList.as_view()),
    path('all/', views.AllSpecialistList.as_view()),
    path('time/', views.ReturnTimeList.as_view()),
]