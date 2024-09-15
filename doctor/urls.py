from django.urls import path

from doctor import views

urlpatterns = [
    path('specialist/', views.SpecialistList.as_view()),
    path('all/', views.AllSpecialistList.as_view()),
    path('time/', views.ReturnTimeList.as_view()),
]