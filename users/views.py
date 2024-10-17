from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from .models import  CustomUser
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth import login, authenticate, logout
import logging
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email = EmailMessage(
                subject,
                message,
                'samtech.websites@gmail.com',
                [user.email],
            )
            email.content_subtype = "html"
            email.send()
            return redirect('users:activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'users/register.html', {'form': form})
@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')
def activation_sent(request):
    return render(request, 'users/activation_sent.html')

def activation_invalid(request):
    return render(request, 'users/activation_invalid.html')

def home(request):
    return render(request, 'users/home.html')  # Ensure this view is defined

def about(request):
    return render(request, 'users/about.html')

def contact(request):
    return render(request, 'users/contact.html')



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'users/activation_invalid.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')


"""
@csrf_exempt
@require_POST
def add_mpesa_transaction(request):
    # if not request.user.is_staff:
    #     return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    mpesa_message = request.POST.get('mpesa_message')
    if not mpesa_message:
        return JsonResponse({'error': 'M-Pesa message is required'}, status=400)
    
    transaction_id, amount, transaction_date, phone_number = extract_mpesa_details(mpesa_message, action='add')
    
    if transaction_id and amount and transaction_date and phone_number:
        transaction, created = Payment.objects.get_or_create(
            transaction_id=transaction_id,
            defaults={
                'amount': amount,
                'phone_number': phone_number,
                'transaction_date': transaction_date
            }
        )
        
        if created:
            return JsonResponse({'message': 'Transaction added successfully'})
        else:
            return JsonResponse({'message': 'Transaction already exists'})
    else:
        return JsonResponse({'error': 'Invalid M-Pesa message'}, status=400)
"""
def custom_error_handler(request, reason=""):
    # Log the error reason if you want
    print(f"\nError occurred: {reason}\n")

    messages.error(request, "An error occurred. You've been redirected to the homepage.")

    return redirect(reverse('home'))