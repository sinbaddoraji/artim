from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserLoginForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.hashers import make_password

def user_login(request):
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
                    else:
                        return redirect('accounts:dashboard')
                else:
                    return render(request, 'login.html', context={'form':form})

    return render(request, 'accounts/login.html', context={'form': form})


def user_register(request):
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
    return redirect('index')

class Dashboard(TemplateView):
    template_name = 'accounts/dashboard.html'

class Success(TemplateView):
    template_name = 'accounts/registration_successful.html'