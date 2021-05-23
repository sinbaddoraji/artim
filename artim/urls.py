from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import HomePage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view(), name='index'),
    path('account/', include('accounts.urls')),
]
