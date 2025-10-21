from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, Favorite
from .forms import ReviewForm
from bookings.models import Booking
from accounts.models import ArtistProfile

# NOTE: The incorrect, conflicting 'class Review(models.Model):' has been
# PERMANENTLY REMOVED from this file. This is the entire fix.

@login_required
def add_review_view(request, booking_id):
    """
    Allows an organizer to add a review for a completed booking.
    """
    booking = get_object_or_404(Booking, pk=booking_id, organizer=request.user)
    
    if Review.objects.filter(booking=booking).exists():
        messages.error(request, 'You have already submitted a review for this booking.')
        return redirect('organizer_bookings') # Redirect to a valid page

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.artist = booking.artist
            review.organizer = request.user
            review.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect('dashboard')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'booking': booking,
        'artist': booking.artist.artistprofile,
    }
    return render(request, 'reviews/add_review.html', context)

@login_required
def toggle_favorite_view(request, artist_id):
    """
    Adds or removes an artist from an organizer's favorites list.
    """
    if not request.user.role == 'ORGANIZER':
        messages.error(request, 'Only organizers can have favorites.')
        return redirect('artist_profile', artist_id=artist_id)
        
    artist_user = get_object_or_404(ArtistProfile, pk=artist_id).user
    organizer_user = request.user
    
    favorite, created = Favorite.objects.get_or_create(organizer=organizer_user, artist=artist_user)
    
    if created:
        messages.success(request, f'{artist_user.artistprofile.contact_name} has been added to your favorites!')
    else:
        favorite.delete()
        messages.success(request, f'{artist_user.artistprofile.contact_name} has been removed from your favorites.')
        
    return redirect('artist_profile', artist_id=artist_id)

