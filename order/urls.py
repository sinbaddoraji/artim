from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('placeorder/<slug:slug>', views.order_service, name="place_order"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('makepayment/', views.payment_page, name='payment_page'),
    path('paymentcompleted/', views.payment_completed, name='payment_completed'),
    path('paymentcancelled/', views.payment_canceled, name='payment_cancelled'),
    path('request/<str:action><int:order>/', views.accept_or_reject_request, name='accept_or_reject'),
    path('addfunds/<str:amount>/', views.add_funds_to_account, name='add_funds'),
    path('addfundscomplete/<str:amount>/<str:key>/', views.addfunds_payment_completed, name='added_funds'),
    path('funds/paymentcompleted/', views.payment_completed_with_funds, name='payment_completed_with_funds'),
    path('withdrawfunds/', views.withdraw_funds, name='withdraw_funds'),
    path('api/getbtcaddress/', views.getBitcoinAddress)
]