from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('placeorder/<slug:slug>', views.order_service, name="place_order"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('makepayment/', views.payment_page, name='payment_page'),
    path('paymentcompleted/', views.payment_completed, name='payment_completed'),
    path('paymentcancelled/', views.payment_canceled, name='payment_cancelled'),
]