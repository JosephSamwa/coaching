from django.urls import path, include
from users.views import home, register, login_view, logout_view, dashboard
from courses.views import course_list, lesson_view, user_courses, course_detail, enroll
from payments.views import initiate_payment, payment_success, payment_failure, payment_history

app_name = 'courses'

urlpatterns = [
    # Home
    path('', home, name='home'),

    # User Authentication
    path('signup/', register, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Courses
    path('courses/', course_list, name='course_list'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', lesson_view, name='lesson_view'),
    path('my-courses/', user_courses, name='user_courses'),
    path('enroll/<int:course_id>/', enroll, name='enroll'),

    # User Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # Payments
    path('payments/', include('payments.urls')),
    path('payments/initiate/<int:course_id>/', initiate_payment, name='initiate_payment'),
    path('payments/success/<int:payment_id>/', payment_success, name='payment_success'),
    path('payments/failure/', payment_failure, name='payment_failure'),
    path('payments/history/', payment_history, name='payment_history'),
]