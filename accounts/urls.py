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
    path('deleteaccount/<slug:slug>/', views.DeleteUserView.as_view(), name='deleteaccount'),
    path('addbankaccount/', views.add_bank_details, name='add_bank_details'),
    path('admin/<slug:username>/<slug:action>/', views.approve_or_block_user_view, name='approve_or_block'),
    path('admin/blockedusers/', views.BlockUsers.as_view(), name='blocked_users'),
    path('admin/manageartisans/', views.ManageArtisansView.as_view(), name='manage_artisans'),
    path('admin/managecustomers/', views.ManageCustomersView.as_view(), name='manage_customers'),
    path('admindeleteuser/<slug:slug>/', views.AdminDeleteUserView.as_view(), name='admin_deleteaccount'),
    path('social/completeprofile/', views.CompleteProfile.as_view(), name='social_complete_profile'),
    path('withdrawals/', views.WithdrawListView.as_view(), name='withdrawal_list_view')
]