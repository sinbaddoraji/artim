from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from accounts.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import SKILLS

class HomePage(ListView):
    context_object_name = 'artisans'
    template_name = 'index.html'
    slug = "home"

    def get(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('slug')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = UserProfile.objects.filter(user_type='artisan')
        if self.slug == "home" or self.slug == "all":
            return queryset
        else:
            return queryset.filter(services__contains=self.slug)
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['skills'] = SKILLS
        return context

def redirect_to_home(request):
    return redirect('/home/')

class UserDetailView(DetailView):
    model = UserProfile
    slug_field = 'slug'
    template_name = 'user_detail.html'
    