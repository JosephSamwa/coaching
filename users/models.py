from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    enrollments = models.ManyToManyField('courses.Course', related_name='users')  # Use string reference
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True)  # Use string reference
    payment_status = models.CharField(max_length=20, default='Pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_time = models.DateTimeField(null=True, blank=True)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True)  # Use string reference

    def __str__(self):
        return self.user.username
