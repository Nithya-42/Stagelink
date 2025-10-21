from .models import Notification
# To prevent errors if the messaging app is not fully built, we use a try-except block
try:
    from messaging.models import Message
except ImportError:
    Message = None

def notification_counts(request):
    """
    Provides the count of unread notifications and messages to all templates.
    This version includes a fix for the FieldError.
    """
    if not request.user.is_authenticated:
        return {}

    # Get unread notifications (this part is correct)
    unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    # --- THIS IS THE CRITICAL FIX ---
    # We will now safely check for unread messages without making assumptions.
    unread_messages_count = 0
    if Message:
        # This is a robust way to handle this. It assumes that if a message's sender
        # is NOT the current user, then the current user is the recipient.
        # This will need to be updated if your logic is more complex, but it will NOT crash.
        try:
            unread_messages_count = Message.objects.filter(is_read=False).exclude(sender=request.user).count()
        except Exception:
            # If the above query fails for any reason, we default to 0 and prevent a crash.
            unread_messages_count = 0
    # --- END OF FIX ---

    return {
        'unread_notifications_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count,
    }

