from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.models import SavedOrder
from .models import UserOrder, Withdrawal
from accounts.models import SavedOrder
from accounts.models import UserProfile
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random
import requests


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


@login_required
def add_funds_to_account(request, amount):
    if int(amount) > 500:
        messages.error(request, f"You can only add at most £500 at once.")
        return redirect('accounts:dashboard')
    else:
        key = get_random_string(length=10)
        request.session['order'] = {
            'amount': amount,
            'key': key
        }
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': amount,
            'item_name': 'Adding funds to account',
            'invoice': key,
            'currency_code': 'GBP',
            'notify_url': f"http://{host}{reverse('orders:paypal-ipn')}",
            'return_url': f"http://{host}{reverse('orders:added_funds', args=[amount, key])}",
            'cancel_return': f"http://{host}{reverse('orders:payment_cancelled')}",
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        if request.method == "POST":
            UserProfile.objects.filter(user = request.user).update(balance = request.user.userprofile.balance+int(amount))
            messages.success(request, f"Great news! £{amount} has been successfully added to your balance.")
            return redirect('accounts:dashboard')
    return render(request, 'take_payment.html', context={'form':form, 'addfunds':True, 'amount':amount})



@csrf_exempt
@login_required
def addfunds_payment_completed(request, amount, key):
    try:
        order = request.session['order']
        if order['key'] == key:
            UserProfile.objects.filter(user = request.user).update(balance = request.user.userprofile.balance+int(amount))
            messages.success(request, f"Great news! £{amount} has been successfully added to your balance.")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, f"Don't act smart, next time you will be blocked.")
            return redirect('accounts:dashboard')
    except KeyError:
        return redirect('accounts:dashboard')


@login_required
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

    artisan = get_object_or_404(User, username=order['artisan'])
    return render(request, 'take_payment.html', context={'form':form, 'price':order['price'], 'artisan':artisan})


@login_required
def payment_completed_with_funds(request):
    try:
        order = request.session["order"]
        if request.user.userprofile.balance > float(order["price"]):
            artisan = get_object_or_404(User, username=order["artisan"])
            destination = request.user.userprofile.city
            origin = artisan.userprofile.city
            response_driving = requests.post(
                f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=driving'
                )
            response_bicycle = requests.post(
                f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=bicycling'
                )
            response_walking = requests.post(
                f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=walking'
                )
            UserOrder.objects.create(
                            customerorder = request.user.userprofile,
                            artisanorder = artisan.userprofile,
                            service = order["service"],
                            message = order["message"],
                            order_price = order["price"],
                            total_distance = round(response_driving.json()['rows'][0]['elements'][0]['distance']['value']/1000*0.621371, 1),
                            walking_time = response_walking.json()['rows'][0]['elements'][0]['duration']['text'],
                            driving_time = response_driving.json()['rows'][0]['elements'][0]['duration']['text'],
                            bicycle_time = response_bicycle.json()['rows'][0]['elements'][0]['duration']['text']
                        )
            UserProfile.objects.filter(user = request.user).update(balance = request.user.userprofile.balance - int(float(order["price"])))
            del request.session["order"]
        else:
            return redirect('accounts:dashboard')
    except KeyError:
        return redirect('accounts:dashboard')
    return render(request, 'payment_completed.html')


@csrf_exempt
@login_required
def payment_completed(request):
    try:
        order = request.session["order"]
        artisan = get_object_or_404(User, username=order["artisan"])
        destination = request.user.userprofile.city
        origin = artisan.userprofile.city
        response_driving = requests.post(
            f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=driving'
            )
        response_bicycle = requests.post(
            f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=bicycling'
            )
        response_walking = requests.post(
            f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins="{origin}, UK"&destinations="{destination} UK"&key=AIzaSyDpWjr69HcxTnG5OirZmvl6qvtg2NMpYCM&units=imperial&mode=walking'
            )
        UserOrder.objects.create(
                        customerorder = request.user.userprofile,
                        artisanorder = artisan.userprofile,
                        service = order["service"],
                        message = order["message"],
                        order_price = order["price"],
                        total_distance = round(response_driving.json()['rows'][0]['elements'][0]['distance']['value']/1000*0.621371, 1),
                        walking_time = response_walking.json()['rows'][0]['elements'][0]['duration']['text'],
                        driving_time = response_driving.json()['rows'][0]['elements'][0]['duration']['text'],
                        bicycle_time = response_bicycle.json()['rows'][0]['elements'][0]['duration']['text']
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
            UserProfile.objects.filter(user = order.artisanorder).update(balance = order.artisanorder.balance+order.order_price)
            order.completed()
            try:
                send_mail(
                        f'Your service rendered has been marked as completed',
                        f"Hi {order.artisanorder.user.first_name}, {order.customerorder.user.first_name} has marked your service as completed and your funds have been deposited to your account. Thanks working with ARTIM",
                        'ARTIM <noreply@yankeytechnologies.topeyankey.com>',
                        [order.artisanorder.user.email],
                    )
            except:
                pass
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
                try:
                    send_mail(
                        f'Your order request for {order.service} has been accepted',
                        f"Hi {order.customerorder.user.first_name}, you request for {order.artisanorder.user.first_name}'s service on ARTIM. We are sending this email to inform you that your request has been accepted",
                        'ARTIM <noreply@yankeytechnologies.topeyankey.com>',
                        [order.customerorder.user.email],
                    )
                except:
                    pass
                messages.success(request, f"Request has been accepted, please contact the Customer with the information shown.")
                return redirect('accounts:dashboard')
            elif action == "reject":
                order = UserOrder.objects.get(pk=order)
                order.rejected()
                UserProfile.objects.filter(user = order.customerorder).update(balance = order.customerorder.balance+order.order_price)
                try:
                    send_mail(
                    f'Your order request for {order.service} has been rejected',
                    f"Hi {order.customerorder.user.first_name}, we are sorry to let you know that {order.artisanorder.user.first_name} has rejected your request for {order.service}. Please check out another artisan",
                    'ARTIM <noreply@yankeytechnologies.topeyankey.com>',
                    [order.customerorder.user.email],
                )
                except:
                    pass
                messages.error(request, f"The customer has been notified of the decline")
                return redirect('accounts:dashboard')
        else:
            messages.error(request, f"You can't access that page, If you attempt that again you might be blocked.")
            return redirect('accounts:dashboard')


def withdraw_funds(request):
    if request.user.userprofile.balance < 5:
        return redirect('accounts:dashboard')
    else:
        bank_info = request.user.userprofile.bank_details[2:-2].split(", ")
        bank = {
            'bank': bank_info[0],
            'sort_code': f'{bank_info[1][:2]}-{bank_info[1][2:4]}-{bank_info[1][4:]}',
            'account': bank_info[2][-2:]
        }
        url = 'https://blockchain.info/ticker'
        bitcoin_price = requests.get(url).json()['GBP']
        if request.method == 'POST':
            withdraw_method = request.POST.get("method")
            amount = request.POST.get("amount")
            password = request.POST.get("password")
            if not check_password(password, request.user.password):
                if withdraw_method == 'bank':
                    return render(
                        request, 'withdraw_funds.html', 
                        context={
                            'bank':bank, 
                            'btc':bitcoin_price, 
                            'bank_password_error': 'You entered a wrong password',
                            'bank_check': 'checked'
                            }
                        )
                else:
                    return render(
                        request, 'withdraw_funds.html', 
                        context={
                            'bank':bank, 
                            'btc':bitcoin_price, 
                            'bitcoin_password_error': 'You entered a wrong password',
                            'bitcoin_check': 'checked'
                            }
                        )
            elif int(amount) > request.user.userprofile.balance:
                if withdraw_method == 'bank':
                    return render(
                        request, 'withdraw_funds.html', 
                        context={
                            'bank':bank, 
                            'btc':bitcoin_price, 
                            'bank_amount_error': "You can't withdraw an amount more than your balance",
                            'bank_check': 'checked'
                            }
                        )
                else:
                    return render(
                        request, 'withdraw_funds.html', 
                        context={
                            'bank':bank, 
                            'btc':bitcoin_price, 
                            'bitcoin_amount_error': "You can't withdraw an amount more than your balance",
                            'bitcoin_check': 'checked'
                            }
                        )
            else:
                UserProfile.objects.filter(user = request.user).update(balance = request.user.userprofile.balance - int(amount))
                Withdrawal.objects.create(
                    artisanwithdrawal = request.user.userprofile,
                    amount = amount,
                    method = withdraw_method
                )
                return render(request, 'withdraw_funds.html', context={'successfull':True, 'method':withdraw_method, 'amount':amount}) 
        return render(request, 'withdraw_funds.html', context={'bank':bank, 'btc':bitcoin_price})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBitcoinAddress(request):
    response = requests.get('https://block.io//api/v2/get_my_addresses/?api_key=bb4d-1544-8e7b-5458').json()
    bitcoin_price = requests.get('https://blockchain.info/ticker').json()['GBP']
    addresses = response['data']['addresses']
    return Response({'price':bitcoin_price['15m'], 'wallet':addresses[random.randint(0, len(response['data']['addresses'])-1)]['address']})