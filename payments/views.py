from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Payment
from courses.models import Course, Enrollment
from .forms import PaymentForm  # Import the PaymentForm
from django.contrib import messages
import logging
from users.models import UserProfile
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import extract_mpesa_details
logger = logging.getLogger(__name__)


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

@login_required
@csrf_exempt
def initiate_payment(request, course_id):
    try:
        logger.debug(f"Received course_id: {course_id}")
        course = get_object_or_404(Course, id=course_id)
        logger.debug(f"Course found: {course}")
        
        # Check if the user is already enrolled
        user_profile = request.user.userprofile
    except Course.DoesNotExist:
        messages.error(request, "The requested course does not exist.")
        return redirect('some_error_page')
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()  # Save the new UserProfile instance
 
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=user_profile, course_fee=course.price)
        if form.is_valid():
            try:
                payment = form.save(commit=False)
                mpesa_message = form.cleaned_data.get('mpesa_message', '')
                phone_number = form.cleaned_data.get('phone_number', '')
 
                fee = course.price
                payment.fee_paid = fee
                
                transaction_id, amount, transaction_date, _ = extract_mpesa_details(mpesa_message, action='verify')
 
                if not (transaction_id and amount and transaction_date and phone_number):
                    raise ValueError("Invalid M-Pesa message")
 
                if amount != fee:
                    raise ValueError("Amount mismatch")
 
                transaction = Payment.objects.get(transaction_id=transaction_id)
                
                if transaction.is_used:
                    raise ValueError("Transaction already used")
                
                if transaction.phone_number != phone_number:
                    raise ValueError("Transaction details mismatch")
 
                transaction.transaction_date = timezone.now()
                transaction.status = 'completed'
                payment.save()
                transaction.is_used = True
                transaction.save()
                Enrollment.objects.create(user=request.user, course=course)
                messages.success(request, "Payment successful!")
 
                # Redirect to the payment success page with the payment ID
                return redirect(reverse('payments:payment_success', kwargs={'payment_id': payment.id}))
 
            except Payment.DoesNotExist:
                messages.error(request, "We couldn't find this transaction in our records. Please check your M-Pesa message and try again.")
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                messages.error(request, "An unexpected error occurred. Please try again later or contact support.")
    else:
        logger.debug("GET request received")
        form = PaymentForm(course_fee=course.price)
 
    logger.debug(f"Rendering form with course: {course}")
    return render(request, 'payments/initiate_payment.html', {'form': form, 'course': course})

@login_required
def payment_success(request, payment_id):
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        logger.info(f"Payment success view accessed for payment_id: {payment_id}")
        return render(request, 'payments/payment_success.html', {'payment_id': payment_id, 'payment': payment})
    except Payment.DoesNotExist:
        logger.error(f"Payment with id {payment_id} not found")
        messages.error(request, "Payment not found.")
        return redirect('payments:payment_failure')

@login_required
def payment_failure(request):
    return render(request, 'payments/payment_failure.html', {'error': 'Payment failed. Please try again.'})

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/payment_history.html', {'payments': payments})
