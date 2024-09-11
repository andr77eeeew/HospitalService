from django.urls import path

from users import views

urlpatterns = [
    path('patient-registration/', views.PatientRegisterView.as_view(), name='patient-registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('detail/', views.UserDetailView.as_view(), name='detail'),

    path('doctor/create/', views.DoctorRegisterView.as_view(), name='doctor-create'),
    path('doctor/update/', views.DoctorUpdateView.as_view(), name='doctor-update'),
    path('doctor/key-validate/', views.DoctorKeyValidatorView.as_view(), name='doctor-key-validator'),
]