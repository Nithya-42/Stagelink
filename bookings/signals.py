from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Notification

@receiver(post_save, sender=Booking)
def create_or_update_booking_notification(sender, instance, created, **kwargs):
    """
    Creates a notification when a booking is made or its status is updated.
    """
    if created:
        # Organizer is a User → use username or organizerprofile.contact_name
        organizer_name = (
            getattr(instance.organizer, "organizerprofile", None)
            and instance.organizer.organizerprofile.full_name
        ) or instance.organizer.get_full_name() or instance.organizer.username

        message = f"{organizer_name} has sent you a booking request for {instance.event_date.strftime('%d %b, %Y')}."
        Notification.objects.create(
            recipient=instance.artist,
            sender=instance.organizer,
            message=message,
            related_booking=instance
        )
    else:
        # A booking was updated (accepted/declined), notify the ORGANIZER
        artist_name = instance.artist.artistprofile.contact_name

        if instance.status == 'ACCEPTED':
            message = f"{artist_name} has ACCEPTED your booking request."
            Notification.objects.create(
                recipient=instance.organizer,
                sender=instance.artist,
                message=message,
                related_booking=instance
            )
        elif instance.status == 'DECLINED':
            message = f"{artist_name} has DECLINED your booking request."
            Notification.objects.create(
                recipient=instance.organizer,
                sender=instance.artist,
                message=message,
                related_booking=instance
            )
