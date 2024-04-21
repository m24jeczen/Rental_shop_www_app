from .models import RentalRecord, Car
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RentalRecordForm(forms.ModelForm):
    car = forms.ModelChoiceField(queryset=Car.objects.none(), widget=forms.HiddenInput())

    class Meta:
        model = RentalRecord
        fields = ['start_date', 'end_date', 'car']

    def __init__(self, *args, **kwargs):
        car_id = kwargs.pop('car_id', None)
        super(RentalRecordForm, self).__init__(*args, **kwargs)
        if car_id:
            self.fields['car'].queryset = Car.objects.filter(id=car_id)




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1, self.instance)
        except ValidationError as error:
            self.add_error("password1", error)
        return password1

from .models import CustomerProfile

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['contact_number', 'address', 'driving_license']

