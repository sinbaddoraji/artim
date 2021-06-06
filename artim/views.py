from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
from django.urls import reverse
from accounts.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from accounts.forms import SKILLS
from .forms import ReviewForm
from django.contrib import messages

def homepage(request):
    return render(request, 'homepage.html')

class ArtisanListView(ListView):
    context_object_name = 'artisans'
    template_name = 'index.html'
    slug = "home"
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        self.slug = self.kwargs.get('slug')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = UserProfile.objects.filter(user_type='artisan').filter(artisan_approved=True).filter(blocked=False).order_by('-pk')
        if self.slug == "home" or self.slug == "all":
            return queryset
        else:
            return queryset.filter(services__contains=self.slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = SKILLS
        return context


class UserDetailView(FormMixin, DetailView):
    model = UserProfile
    slug_field = 'slug'
    template_name = 'user_detail.html'
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('user-detail', kwargs={'slug': self.object.slug, 'user_type':self.object.user_type})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            messages.success(request, 'Your review was submitted successfully.')
            return self.form_valid(form)
        else:
            messages.error(request, 'Your review was not submitted, please fill in the form properly and then resubmit.')
            return self.form_invalid(form)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.artisan_review = self.object
        review.customer_review = self.request.user.userprofile
        review.save()
        return super().form_valid(form)


def goodbye(request):
    return render(request, 'user_delete_successful.html')
    
