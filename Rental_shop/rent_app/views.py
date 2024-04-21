from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.contrib.auth import logout
from .models import Car, RentalRecord, CustomerProfile
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Car
from .forms import RentalRecordForm, CustomerProfileForm
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from xml.etree.ElementTree import Element, SubElement, tostring

def home(request):
    available_cars = Car.objects.filter(is_rented=False)
    print("Home view called, cars:", available_cars)  # For debugging
    return render(request, 'rent_app/home.html', {'cars': available_cars})


@login_required
def profile(request):
    try:
        customer_profile = request.user.customerprofile
    except CustomerProfile.DoesNotExist:
        customer_profile = CustomerProfile(user=request.user)

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=customer_profile)

    rentals = RentalRecord.objects.filter(user=request.user)
    return render(request, 'rent_app/profile.html', {'form': form, 'rentals': rentals})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect('/rent_app/profile/')
    else:
        form = AuthenticationForm()
    return render(request, 'rent_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/rent_app/home/')


@login_required
def rent_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, is_rented=False)
    if request.method == 'POST':
        form = RentalRecordForm(request.POST, car_id=car_id)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.car = car
            rental_period = rental.end_date - rental.start_date
            rental.total_cost = rental.car.daily_rate * rental_period.days

            try:
                rental.full_clean()
                rental.save()
                car.is_rented = True
                car.save()
                messages.success(request, "Car rented successfully.")
                return redirect('profile')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)

    else:
        form = RentalRecordForm(car_id=car_id, initial={'car': car})

    context = {
        'form': form,
        'selected_car': car,
        'form_submitted': request.method == 'POST'
    }
    return render(request, 'rent_app/rental_form.html', context)



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Rent-a-Car Account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            activation_link = f"http://{current_site.domain}/rent_app/activate/{uid}/{token}/"

            message = render_to_string('rent_app/activation_email.html', {
                'user': user,
                'activation_link': activation_link
            })
            send_mail(subject, message, 'from@example.com', [user.email], fail_silently=False)

            return HttpResponseRedirect('/rent_app/account_activation_sent')
    else:
        form = CustomUserCreationForm()
    return render(request, 'rent_app/register.html', {'form': form})

@login_required
def return_car(request, rental_id):
    rental = RentalRecord.objects.filter(id=rental_id, user=request.user).first()
    if not rental:
        return HttpResponseForbidden("You cannot return a car you did not rent.")

    car = rental.car
    car.is_rented = False
    car.save()
    rental.delete()
    return HttpResponseRedirect('/rent_app/profile/')



def export_cars_xml(request):
    cars = Car.objects.all()
    root = Element('Cars')

    for car in cars:
        car_element = SubElement(root, 'Car')
        make = SubElement(car_element, 'Make')
        make.text = car.make
        model = SubElement(car_element, 'Model')
        model.text = car.model
        year = SubElement(car_element, 'Year')
        year.text = str(car.year)
        daily_rate = SubElement(car_element, 'DailyRate')
        daily_rate.text = str(car.daily_rate)

    response = HttpResponse(tostring(root), content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="cars.xml"'
    return response

import xlwt
from django.http import HttpResponse

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Username', 'First name', 'Last name', 'Email']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User

@csrf_exempt
def validate_field(request):
    data = json.loads(request.body)
    field_name = data['fieldName']
    value = data['value']

    field_data = {field_name: value}

    form = CustomUserCreationForm(field_data)

    if form.is_valid() or field_name not in form.errors:
        return JsonResponse({'is_valid': True})
    else:
        error = form.errors[field_name][0]
        return JsonResponse({'is_valid': False, 'error': error})

def account_activation_sent(request):
    return render(request, 'rent_app/account_activation_sent.html')




def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('some-success-page')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('home')

def some_success_view(request):
    return render(request, 'rent_app/some_success_page.html')
