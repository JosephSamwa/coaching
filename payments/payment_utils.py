from django.utils import timezone
from django.core.exceptions import ValidationError

def get_prep_value(self, value):
    if value is None:
        return None
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValidationError(f"Field '{self.name}' expected a number but got a string that couldn't be converted: {value!r}")
    
    if isinstance(value, timezone.datetime):
        return int(value.timestamp())
    
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Field '{self.name}' expected a number but got {type(value).__name__}: {value!r}")
    

    # payments/payment_utils.py

import logging

logger = logging.getLogger(__name__)

def process_payment(payment):
    """
    Process the payment.
    
    This is a placeholder function. You should implement the actual payment processing logic here.
    
    Args:
        payment (Payment): The payment instance to be processed.
    
    Returns:
        bool: True if the payment was processed successfully, False otherwise.
    """
    try:
        # Example logic for processing the payment
        logger.info(f"Processing payment for user {payment.user.username} for course {payment.course.title}")
        
        # Simulate payment processing
        payment.status = 'completed'
        payment.save()
        
        logger.info(f"Payment processed successfully for user {payment.user.username}")
        return True
    except Exception as e:
        logger.error(f"Error processing payment for user {payment.user.username}: {e}")
        payment.status = 'failed'
        payment.save()
        return False
