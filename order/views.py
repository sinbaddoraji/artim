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
        return render(request, 'order_form.html', context={'artisan':slug, 'services':services})
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

    return render(request, 'take_payment.html', context={'form':form, 'price':order['price'], 'artisan':order['artisan']})


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