from django.urls import path, include
from . import views
from courses.views import course_list, user_course_details, course_detail, enroll
from payments.views import add_mpesa_transaction, initiate_payment, payment_success, payment_failure as payments_payment_failure, payment_history

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('payment_failure/', payments_payment_failure, name='payment_failure'),
    path('payments/success/<int:payment_id>/', payment_success, name='payment_success'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('payments/', include('payments.urls')),
    path('list/', course_list, name='course_list'),
    path('course/<int:course_id>/enroll/', enroll, name='enroll'),
    #path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.register, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_course_details/', user_course_details, name='user_course_details'),
    path('payments/history/', payment_history, name='payment_history'),
    path('payments/initiate/<int:course_id>/', initiate_payment, name='initiate_payment'),
    path('add-mpesa-transaction/', add_mpesa_transaction, name='add_mpesa_transaction'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation_sent/', views.activation_sent, name='activation_sent'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    #path('users/', include('django.contrib.auth.urls')),
]
