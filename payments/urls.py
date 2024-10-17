from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('initiate/<int:course_id>/', views.initiate_payment, name='initiate_payment'),
    path('failure/', views.payment_failure, name='payment_failure'),
    path('history/', views.payment_history, name='payment_history'),
    path('add-mpesa-transaction/', views.add_mpesa_transaction, name='add_mpesa_transaction'),
]
