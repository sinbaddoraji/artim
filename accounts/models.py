from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_resized import ResizedImageField


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="userprofile",on_delete=models.CASCADE)
    photo = ResizedImageField(size=[400, 400], crop=['middle', 'center'], quality=100, force_format='JPEG', upload_to='images', blank=True, null=True)
    gender = models.CharField(max_length=10)
    age = models.PositiveSmallIntegerField()
    payment_details = models.CharField(max_length=100, null=True, blank=True)
    bank_details = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    user_type = models.CharField(max_length=10)
    services = models.CharField(max_length=100, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.user.first_name.title()} ({self.user_type.upper()})"

    def get_rating(self):
        if self.artisan_review.count() == 0:
            return 0
        return round(((sum(i.rating for i in self.artisan_review.all()))/self.artisan_review.count()), 1)
    
    def get_total_reviews(self):
        return self.artisan_review.count()


class Review(models.Model):
    artisan_review = models.ForeignKey(UserProfile, related_name='artisan_review', on_delete=models.CASCADE)
    customer_review = models.ForeignKey(UserProfile, related_name='customer_review', on_delete=models.CASCADE)
    rating = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    comment = models.TextField()
    review_date = models.DateTimeField(default=timezone.now)


class Order(models.Model):
    customer_order = models.ForeignKey(UserProfile, related_name='customer_order', on_delete=models.CASCADE)
    artisan_order = models.ForeignKey(UserProfile, related_name='artisan_order', on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    order_date = models.DateTimeField(default=timezone.now)
    order_price = models.DecimalField(decimal_places=2, max_digits=10)


class Basket(models.Model):
    service = models.CharField(max_length=100)
    artisan = models.ForeignKey(User, on_delete=models.CASCADE)