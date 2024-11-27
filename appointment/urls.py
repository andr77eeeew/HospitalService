from django.urls import path
from appointment import views

urlpatterns = [
    path('create/', views.CreateAppointmentView.as_view()),
    path('get/', views.GetUpcomingAndRecentAppointmentsView.as_view()),
    path('get-all/', views.GetAppointmentForUserView.as_view()),
    path('delete/', views.DeleteAppointmentView.as_view()),
]
