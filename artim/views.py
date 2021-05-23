from django.shortcuts import render
from django.views.generic import ListView
from accounts.models import UserProfile

class HomePage(ListView):
    queryset = UserProfile.objects.filter(user_type='artisan')
    template_name = 'index.html'