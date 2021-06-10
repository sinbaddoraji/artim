from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_resized import ResizedImageField
from django.utils.text import slugify
from django.shortcuts import redirect


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="userprofile",on_delete=models.CASCADE)
    slug = models.SlugField()
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
    services = models.CharField(max_length=100, null=True, blank=True)
    artisan_approved = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.user.username)
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __str__(self):
        return f"{self.user.first_name.title()} ({self.user_type.upper()})"

    def get_rating(self):
        if self.artisan_review.count() == 0:
            return 0
        return round(((sum(i.rating for i in self.artisan_review.all()))/self.artisan_review.count()), 1)
    
    def get_total_reviews(self):
        return self.artisan_review.count()

    def approve_artisan(self):
        self.user.is_active = True
        self.user.save()
        self.artisan_approved = True
        self.blocked = False
        self.save()

    def block_user(self):
        self.user.is_active = False
        self.user.save()
        self.blocked = True
        self.save()

    def unblock_user(self):
        self.user.is_active = True
        self.user.save()
        self.blocked = False
        self.save()


class Review(models.Model):
    artisan_review = models.ForeignKey(UserProfile, related_name='artisan_review', on_delete=models.CASCADE)
    customer_review = models.ForeignKey(UserProfile, related_name='customer_review', on_delete=models.CASCADE)
    rating = models.DecimalField(decimal_places=2, max_digits=10)
    comment = models.TextField()
    review_date = models.DateTimeField(default=timezone.now)



class SavedOrder(models.Model):
    service = models.CharField(max_length=100)
    artisan_basket = models.ForeignKey(UserProfile, related_name='artisan_basket', on_delete=models.CASCADE)
    customer_basket = models.ForeignKey(UserProfile, related_name='customer_basket', on_delete=models.CASCADE)