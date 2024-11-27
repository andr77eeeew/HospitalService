from django.urls import path

from users import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('detail/', views.UserDetailView.as_view(), name='detail'),
    path('update/', views.UserUpdateView.as_view(), name='update'),
    path('specific/', views.GetSpecificUserView.as_view(), name='specific'),
    path('subroles/', views.GetSubRolesView.as_view(), name='users-subroles'),
    path('request-reset/', views.RequestPasswordReset.as_view(), name='request-reset'),
    path('reset-password/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('admin/users/', views.UsersForAdmin.as_view(), name='admin-users'),
    path('admin/block/', views.BlockUserView.as_view(), name='admin-roles'),
]
