from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import UserDetailView, goodbye
from django.contrib.auth import views as auth_views
from .views import ArtisanListView, homepage, AlternativeArtisanView
from accounts.views import SocialDashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset_form.html',
            subject_template_name='password_reset_subject.txt',
            email_template_name='password_reset_email.html'
            ),
        name='password_reset',
    ),
    path(
        'password-reset-done/',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'
    ),
    path('', homepage, name='homepage'),
    path('<slug>/', ArtisanListView.as_view(), name='index'),
    path('<str:searched>/<slug:slug>/', AlternativeArtisanView.as_view(), name='alternative'),
    path('account/', include('accounts.urls')),
    path('order/', include('order.urls')),
    path('profile/<str:user_type>/<slug:slug>/', UserDetailView.as_view(), name='user-detail'),
    path('user/goodbye/', goodbye, name='goodbye'),
    path('accounts/profile/', SocialDashboard.as_view(), name='social_dashboard'),
    path('external/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)