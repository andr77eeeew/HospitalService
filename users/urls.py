from django.urls import path

from users import views

urlpatterns = [
    path('patient-registration/', views.PatientRegisterView.as_view(), name='patient-registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('detail/', views.UserDetailView.as_view(), name='detail'),
]