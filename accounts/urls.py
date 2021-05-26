<<<<<<< HEAD
from django.urls import path, include
=======
from django.urls import path
from django.contrib.auth import views as auth_views
>>>>>>> 38cc73affc8be3f0a19e2a7c2b532057cbbb581c
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.userlogout, name='logout'),
<<<<<<< HEAD
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('success/<str:info>/', views.Success.as_view(), name='success'),
=======
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('changepassword/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html', success_url='/account/changepassword/done'), name='changepassword'),
    path('changepassword/done', views.Change_password_done, name='change_password_done'),
    path('success/<str:info>', views.Success.as_view(), name='success'),
    path('updateprofile/<int:pk>/', views.Profile_update.as_view(), name='updateprofile'),
>>>>>>> 38cc73affc8be3f0a19e2a7c2b532057cbbb581c
]