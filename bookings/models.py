from django.db import models
from django.conf import settings # Use settings to safely import the User model

# Note: We no longer need to import the profile models directly here,
# as we will link everything through the main User model.

class Booking(models.Model):
    """
    Represents a booking request from an Organizer to an Artist.
    This model is now correctly linked to the main User model.
    """
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined" # Renamed from REJECTED for clarity
        COMPLETED = "COMPLETED", "Completed"

    # --- THIS IS THE CRITICAL ARCHITECTURAL FIX ---
    # We now link directly to the User model, not the profile.
    # This simplifies the logic in all views and signals.
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='artist_bookings',
        limit_choices_to={'role': 'ARTIST'} # Ensures only users with the 'ARTIST' role can be booked
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='organizer_bookings',
        limit_choices_to={'role': 'ORGANIZER'} # Ensures only organizers can book
    )
    # --- END OF FIX ---

    event_date = models.DateField()
    event_details = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # We now access the profile through the user relationship
        return f"Booking for {self.artist.artistprofile.contact_name} by {self.organizer.organizerprofile.full_name}"
    
    def __str__(self):
    artist_name = getattr(self.artist.artistprofile, "contact_name", self.artist.email)
    organizer_name = getattr(self.organizer.organizerprofile, "full_name", self.organizer.email)
    return f"Booking for {artist_name} by {organizer_name}"

class Notification(models.Model):
    """
    Represents a notification for a user about a booking or other event.
    """
    # --- THIS IS THE FIX FOR THE NameError ---
    # We now correctly link to the User model using settings.AUTH_USER_MODEL
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    # --- END OF FIX ---
    
    message = models.TextField()
    related_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.recipient.email}: {self.message[:30]}'

    class Meta:
        ordering = ['-created_at']

