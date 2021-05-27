from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserLoginForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import UserProfile

def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    form = UserLoginForm()

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        nextvalue = request.POST.get('next')
        if form.is_valid():
                username = form.cleaned_data.get('username').lower()
                password = form.cleaned_data.get('password')

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    if nextvalue:
                        return redirect(nextvalue)
                        print(nextvalue)
                    else:
                        return redirect('accounts:dashboard')
                else:
                    return render(request, 'accounts/login.html', context={'form':form, 'error':'Please enter a valid username and password combination.'})

    return render(request, 'accounts/login.html', context={'form': form})


def user_register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = UserForm()
    profileform = UserProfileForm()

    if request.method == "POST":
        profileform = UserProfileForm(request.POST, request.FILES)
        form = UserForm(request.POST)
        if form.is_valid() and profileform.is_valid():
            username = form.cleaned_data.get('username').lower()
            password = form.cleaned_data.get('password')

            user = form.save()
            user.username = username
            user.set_password(password)
            
            user_profile = profileform.save(commit=False)
            user_profile.user = user
            
            user.save()
            user_profile.save()
            return redirect('accounts:success', info=form.cleaned_data.get('first_name'))


    return render(request, 'accounts/register.html', context={'form': form, 'profileform': profileform})


@login_required
def userlogout(request):
    logout(request)
    return redirect('/home/')


class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = 'accounts:login'
    template_name = 'accounts/dashboard.html'


class Success(TemplateView):
    template_name = 'accounts/registration_successful.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)


class ProfileUpdateView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    slug_field = 'slug'
    template_name = 'accounts/update_profile.html'
    success_url = '/account/dashboard/'