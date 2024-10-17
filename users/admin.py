from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
#from payments.models import Payment

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

#admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'course')
    search_fields = ('username', 'course')

""""
@admin.register(Payment)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'phone_number', 'transaction_date', 'is_used')
    search_fields = ('transaction_id', 'phone_number', 'transaction_date')
"""