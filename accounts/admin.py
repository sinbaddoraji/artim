from django.contrib import admin
from .models import *


admin.site.register(UserProfile)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(SavedOrder)