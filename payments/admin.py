from django.contrib import admin
from django.db.models import Sum
from .models import Payment, PurchasedItem

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'transaction_date','is_used')
    list_filter = ('status', 'transaction_date')
    search_fields = ('transaction_id', 'user__username', 'phone_number')

    def changelist_view(self, request, extra_context=None):
        # Calculate the sum of all completed payments
        total_amount = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum']
        
        # If there are no completed payments, set total_amount to 0
        total_amount = total_amount or 0
        
        # Add the total amount to the extra_context
        extra_context = extra_context or {}
        extra_context['total_amount'] = total_amount
        
        # Call the superclass changelist_view with the updated context
        return super().changelist_view(request, extra_context=extra_context)

# Correct registration
admin.site.register(Payment,PaymentAdmin)
admin.site.register(PurchasedItem)