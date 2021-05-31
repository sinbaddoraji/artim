from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, UpdateView, DeleteView, RedirectView, ListView, CreateView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import UserProfile
from order.models import UserOrder
from django.core.mail import send_mail

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
                    if not user.userprofile.blocked:
                        login(request, user)
                        if nextvalue:
                            return redirect(nextvalue)
                            print(nextvalue)
                        else:
                            return redirect('accounts:dashboard')
                    else:
                        return render(request, 'accounts/login.html', context={'form':form, 'error':'Sorry your account has been blocked.'})
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
            first_name = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')

            user = form.save()
            user.username = username
            user.set_password(password)
            
            user_profile = profileform.save(commit=False)
            user_profile.user = user
            
            user.save()
            user_profile.save()

            send_mail(
                'Welcome to ARTIM',
                f'Hi {first_name}, thanks for registering on ARTIM, we hope you enjoy using the website.'
                [email],
            )
            return redirect('accounts:success', info=form.cleaned_data.get('first_name'))


    return render(request, 'accounts/register.html', context={'form': form, 'profileform': profileform})


@login_required
def userlogout(request):
    logout(request)
    return redirect('/home/')


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = UserProfile.objects.filter(artisan_approved=False).filter(blocked=False)
        if self.request.user.is_staff:
            context['artisans'] = queryset
            context['usercount'] = UserProfile.objects.count()
            context['customercount'] = UserProfile.objects.filter(user_type="customer").count()
            context['artisancount'] = UserProfile.objects.filter(user_type="artisan").count()
        else:
            if self.request.user.userprofile.user_type == "customer":
                context['customer_orders'] = UserOrder.objects.filter(customerorder=self.request.user.userprofile)
            else:
                context['artisan_orders'] = UserOrder.objects.filter(artisanorder=self.request.user.userprofile)
        return context



class Success(TemplateView):
    template_name = 'accounts/registration_successful.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)


@login_required
def add_bank_details(request):
    if request.method == "POST":
        bank_name = request.POST.get("bank_name")
        sort_code = request.POST.get("sort_code")
        account_number = request.POST.get("account_number")
        if bank_name and sort_code and account_number:
            UserProfile.objects.filter(user=request.user).update(bank_details=f'"[{bank_name}, {sort_code}, {account_number}]"')
            messages.success(request, 'You have successfully added your bank details.')
            return redirect('accounts:dashboard')
        else:
            return render(
                request, 
                'accounts/add_bank_details.html', 
                context={
                    'error':'Please fill in your bank details prorperly',
                    'bank_name': bank_name,
                    'sort_code': sort_code,
                    'account_number': account_number
                    }
                )

    return render(request, 'accounts/add_bank_details.html')


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    slug_field = 'slug'
    template_name = 'accounts/update_profile.html'
    success_url = reverse_lazy('accounts:dashboard')
    success_message = 'GREAT NEWS! Your profile was updated successfully'

    def test_func(self):
        if self.request.user.userprofile.slug == self.kwargs.get('slug'):
            return self.request.user.userprofile


class DeleteUserView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    slug_field = 'username'
    success_url = reverse_lazy('goodbye')
    
    def test_func(self):
        if self.request.user.userprofile.slug == self.kwargs.get('slug'):
            return self.request.user.userprofile



def approve_or_block_user_view(request, username, action):
    if request.user.is_staff:
        user = UserProfile.objects.get(user__username=username)
        if action == "approve":
            user.approve_artisan()
            user.unblock_user()
            messages.success(request, f'You have successfully approved {username}')
            return redirect('accounts:dashboard')
        elif action == "unblock":
            user.unblock_user()
            messages.success(request, f'You have successfully unblocked {username}')
            return redirect('accounts:dashboard')
        else:
            user.block_user()
            messages.success(request, f'You have successfully blocked {username}')
            return redirect('accounts:dashboard')
    else:
        messages.danger(request, 'That was terrible of you. You will be blocked next time you try such.')
        return redirect('accounts:dashboard')
    

class BlockUsers(LoginRequiredMixin, UserPassesTestMixin, ListView):
    context_object_name = 'blocked_artisans'
    template_name = 'accounts/blocked_users.html'

    def get_queryset(self):
        queryset = UserProfile.objects.filter(blocked=True)
        return queryset

    def test_func(self):
        if self.request.user.is_staff:
            return self.request.user.is_staff


class ManageArtisansView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    context_object_name = 'artisans'
    template_name = 'accounts/manage_artisans.html'

    def get_queryset(self):
        queryset = UserProfile.objects.filter(user_type='artisan')
        return queryset

    def test_func(self):
        if self.request.user.is_staff:
            return self.request.user.is_staff


class ManageCustomersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    context_object_name = 'customers'
    template_name = 'accounts/manage_customers.html'

    def get_queryset(self):
        queryset = UserProfile.objects.filter(user_type='customer')
        return queryset

    def test_func(self):
        if self.request.user.is_staff:
            return self.request.user.is_staff

class AdminDeleteUserView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    slug_field = 'username'
    success_url = reverse_lazy('accounts:dashboard')
    
    def test_func(self):
        if self.request.user.is_staff:
            return self.request.user.is_staff

