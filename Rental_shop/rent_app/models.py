from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Car(models.Model):
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_rented = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
class RentalRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def clean(self):
        super().clean()
        if self.start_date and self.end_date:
            if (self.end_date - self.start_date) > timedelta(days=7):
                raise ValidationError("Rental period cannot exceed one week.")
        else:
            raise ValidationError("Both start date and end date are required.")


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    driving_license = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)
    else:
        CustomerProfile.objects.get_or_create(user=instance)