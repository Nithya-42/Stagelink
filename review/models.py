from django.db import models
from django.conf import settings # Use settings for safe User model import
from bookings.models import Booking

# Note: We no longer import Profile models here.

class Review(models.Model):
    """
    Represents a review from an Organizer for an Artist's performance.
    FIX: All ForeignKey fields now correctly point to the User model.
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.organizer.email} for {self.artist.email} - {self.rating} stars'

class Favorite(models.Model):
    """
    Represents an Organizer's action of favoriting an Artist.
    FIX: All ForeignKey fields now correctly point to the User model.
    """
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorited_by')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('artist', 'organizer') # Prevents duplicate favorites

    def __str__(self):
        return f'{self.organizer.email} favorited {self.artist.email}'
