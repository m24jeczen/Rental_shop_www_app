from celery import shared_task
from .models import RentalRecord
from django.utils import timezone

@shared_task
def check_car_return():
    for rental in RentalRecord.objects.filter(end_date__lte=timezone.now(), car__is_rented=True):
        rental.car.is_rented = False
        rental.car.save()