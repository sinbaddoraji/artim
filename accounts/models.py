from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="userprofile",on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images', default='images/avatar.jpg')
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    payment_details = models.CharField(max_length=100, null=True)
    bank_details = models.CharField(max_length=50, null=True)
    phone_number = models.IntegerField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    user_type = models.CharField(max_length=10)
    services = models.CharField(max_length=100, null=True)


class Review(models.Model):
    artisan = models.ForeignKey(User, related_name='artisanreview', on_delete=models.CASCADE)
    customer = models.ForeignKey(User, related_name='customerreview', on_delete=models.CASCADE)
    rating = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    comment = models.TextField()


class Order(models.Model):
    customer = models.ForeignKey(User, related_name='customerorder', on_delete=models.CASCADE)
    artisan = models.ForeignKey(User, related_name='artisanorder', on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    order_price = models.DecimalField(decimal_places=2, max_digits=10)


class Basket(models.Model):
    service = models.CharField(max_length=100)
    artisan = models.ForeignKey(User, on_delete=models.CASCADE)