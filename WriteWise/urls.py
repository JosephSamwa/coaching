from django.contrib import admin
from django.urls import path, include
from users.views import about, contact, activation_invalid, home, register, login_view, logout_view, dashboard
from courses.views import user_courses, lesson_view, user_course_details, course_detail, enroll
from payments.views import add_mpesa_transaction, initiate_payment, payment_success, payment_failure as payments_payment_failure, payment_history
from users.views import custom_error_handler
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403, handler404, handler500

# Custom error handlers
handler403 = custom_error_handler
handler404 = custom_error_handler
handler500 = custom_error_handler

urlpatterns = [
    path('lesson/<int:lesson_id>/', lesson_view, name='lesson_view'),
    path('my-courses/', user_courses, name='user_courses'),
    path('user_courses/', user_courses, name='user_courses'),  # This can be removed as it's a duplicate
    path('add-mpesa-transaction/', add_mpesa_transaction, name='add_mpesa_transaction'),
    path('about/', about, name='about'),
    path('activation_invalid/', activation_invalid, name='activation_invalid'),
    path('contact/', contact, name='contact'),
    path('enroll/<int:course_id>/', enroll, name='enroll'),
    path('', home, name='home'),
    path('payment_failure/', payments_payment_failure, name='payment_failure'),
    path('payments/success/<int:payment_id>/', payment_success, name='payment_success'),
    path('admin/', admin.site.urls),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('payments/', include('payments.urls')),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('dashboard/', user_course_details, name='dashboard'),
    path('signup/', register, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('payments/history/', payment_history, name='payment_history'),
    path('payments/initiate/<int:course_id>/', initiate_payment, name='initiate_payment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
