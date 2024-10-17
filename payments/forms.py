from django import forms
from .models import Payment
from users.models import UserProfile

class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,  # Make the field read-only
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number',
        })
    )
    mpesa_message = forms.CharField(widget=forms.Textarea, label='M-Pesa Message')
     
    class Meta:
        model = UserProfile
        fields = ['amount', 'phone_number', 'mpesa_message']
        widgets = {
            'course': forms.HiddenInput(),
        }
   
    def clean_transaction_id(self):
        transaction_id = self.cleaned_data.get('transaction_id')
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            raise forms.ValidationError("This transaction ID has already been used.")
        return transaction_id

    def __init__(self, *args, **kwargs):
        course_fee = kwargs.pop('course_fee', None)
        super().__init__(*args, **kwargs)
        if course_fee is not None:
            self.fields['amount'].initial = course_fee