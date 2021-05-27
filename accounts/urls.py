from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.userlogout, name='logout'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('changepassword/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html', success_url='/account/dashboard/'), name='changepassword'),
    path('success/<str:info>/', views.Success.as_view(), name='success'),
    path('updateprofile/<slug:slug>/', views.ProfileUpdateView.as_view(), name='updateprofile'),
]