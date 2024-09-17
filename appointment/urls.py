from django.urls import path
from appointment import views

urlpatterns = [
    path('create/', views.CreateAppointmentView.as_view()),
    path('get/', views.GetAppointmentForUserView.as_view()),
]