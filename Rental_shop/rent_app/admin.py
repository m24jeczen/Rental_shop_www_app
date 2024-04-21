from django.contrib import admin
from .models import Car, RentalRecord, CustomerProfile

admin.site.register(Car)
admin.site.register(RentalRecord)
admin.site.register(CustomerProfile)