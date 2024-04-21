from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('rent_car/<int:car_id>/', views.rent_car, name='rent_car'),
    path('return_car/<int:rental_id>/', views.return_car, name='return_car'),
    path('export/xml/', views.export_cars_xml, name='export_xml'),
    path('export/xls/', views.export_users_xls, name='export_xls'),
    path('validate_field/', views.validate_field, name='validate_field'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('some-success-page/', views.some_success_view, name='some-success-page'),
]