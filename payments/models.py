from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class TimestampIDField(models.BigAutoField):
    def get_prep_value(self, value):
        if isinstance(value, (int, str)):
            return super().get_prep_value(value)
        if isinstance(value, timezone.datetime):
            return int(value.timestamp())
        return super().get_prep_value(value)


class PurchasedItem(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchased_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.user})"

    class Meta:
        app_label = 'payments'


class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    transaction_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, default=1)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')

    def __str__(self):
        return f"Payment {self.id} : {self.transaction_id} : {self.amount} : {self.phone_number} : {self.transaction_date} : {self.is_used} : {self.user} : {self.course}:{self.status}"

    def get_failure_url(self):
        return 'payment_failure_url'

    def get_success_url(self):
        return 'payment_success_url'

    def get_purchased_items(self):
        yield PurchasedItem(
            name='Course Payment',
            sku='12345',
            quantity=1,
            price=self.amount,
            currency='USD',
        )

    def get_timestamp_as_int(self):
        return int(self.timestamp.timestamp())

    class Meta:
        app_label = 'payments'
