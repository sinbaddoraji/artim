from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import HomePage, redirect_to_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<slug>/', HomePage.as_view(), name='index'),
    path('account/', include('accounts.urls')),
    path('', redirect_to_home),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)