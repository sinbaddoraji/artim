from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.userlogout, name='logout'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('success/<str:info>/', views.Success.as_view(), name='success'),
]