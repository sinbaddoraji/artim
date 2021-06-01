from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.models import SavedOrder
from .models import UserOrder
from accounts.models import SavedOrder
from accounts.models import UserProfile
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


@login_required
def order_service(request, slug):
    if request.user.userprofile.user_type == "customer":
        artisan = get_object_or_404(User, username=slug)
        services = artisan.userprofile.services
        if request.method == "POST":
            explanation = request.POST["explanation"]
            service = request.POST["service"]
            if explanation and service:
                request.session['order'] = {
                    'artisan': artisan.username,
                    'service': service,
                    'message': explanation,
                    'price': str(artisan.userprofile.price)
                }
                return redirect('orders:payment_page')
            else:
                return render(
                    request, 
                    'order_form.html', 
                    context={
                        'error':'Please fill in the form properly.',
                        }
                    )
        return render(request, 'order_form.html', context={'artisan':artisan, 'services':services})
    else:
        messages.error(request, f"You can't access that page, If you attempt that again you might be blocked.")
        return redirect('accounts:dashboard')


def payment_page(request):
    order = request.session['order']
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order["price"],
        'item_name': f'Service from {order["artisan"]}',
        'invoice': get_random_string(length=10),
        'currency_code': 'GBP',
        'notify_url': f"http://{host}{reverse('orders:paypal-ipn')}",
        'return_url': f"http://{host}{reverse('orders:payment_completed')}",
        'cancel_return': f"http://{host}{reverse('orders:payment_cancelled')}",
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    if request.method == "POST":
        return redirect('orders:payment_completed')

    user = get_object_or_404(User, username=order["artisan"])
    return render(request, 'take_payment.html', context={'form':form, 'price':order['price'], 'artisan':order['artisan'], 'user':user})


@csrf_exempt
def payment_completed(request):
    try:
        order = request.session["order"]
        artisan = get_object_or_404(User, username=order["artisan"])
        UserOrder.objects.create(
                        customerorder = request.user.userprofile,
                        artisanorder = artisan.userprofile,
                        service = order["service"],
                        message = order["message"],
                        order_price = order["price"],
                    )
        del request.session["order"]
    except KeyError:
        return redirect('accounts:dashboard')
    return render(request, 'payment_completed.html')


@csrf_exempt
@login_required
def payment_canceled(request):
    try:
        del request.session["order"]
    except KeyError:
        return redirect('accounts:dashboard')
    return render(request, 'payment_canceled.html')


def accept_or_reject_request(request, order, action):
    if action == "completed":
        if request.user.userprofile.user_type == "customer":
            order = UserOrder.objects.get(pk=order)
            order.completed()
            send_mail(
                    f'Your service rendered has been marked as completed',
                    f"Hi {order.artisanorder.user.first_name}, {order.customerorder.user.first_name} has marked your service as completed and your funds have been deposited to your account. Thanks working with ARTIM"
                    [order.artisanorder.user.email],
                )
            messages.success(request, f"Order has been marked as completed. Thanks for using ARTIM")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, f"You can't access that page, If you attempt that again you might be blocked.")
            return redirect('accounts:dashboard')
    else:
        if request.user.userprofile.user_type == "artisan":
            if action == "accept":
                order = UserOrder.objects.get(pk=order)
                order.accepted()
                send_mail(
                    f'Your order request for {order.artisanorder.service} has been accepted',
                    f"Hi {order.customerorder.user.first_name}, you request for {order.artisanorder.user.first_name}'s service on ARTIM. We are sending this email to inform you that your request has been accepted"
                    [order.customerorder.user.email],
                )
                messages.success(request, f"Request has been accepted, please contact the Customer with the information shown.")
                return redirect('accounts:dashboard')
            elif action == "reject":
                order = UserOrder.objects.get(pk=order)
                order.rejected()
                send_mail(
                    f'Your order request for {order.artisanorder.service} has been rejected',
                    f"Hi {order.customerorder.user.first_name}, we are sorry to let you know that {order.artisanorder.user.first_name} has rejected your request for {order.service}. Please check out another artisan"
                    [order.customerorder.user.email],
                )
                messages.error(request, f"Request has been rejected.")
                return redirect('accounts:dashboard')
        else:
            messages.error(request, f"You can't access that page, If you attempt that again you might be blocked.")
            return redirect('accounts:dashboard')

