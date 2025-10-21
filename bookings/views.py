from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Booking, Notification
from accounts.models import ArtistProfile, Availability, OrganizerProfile
from .forms import BookingForm


# --- ORGANIZER VIEWS (ALL QUERIES CORRECTED) ---

@login_required
def organizer_bookings_view(request):
    """Displays all bookings for the logged-in organizer."""
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    # FIX: The query now correctly filters on the User instance 'request.user'.
    bookings = Booking.objects.filter(organizer=request.user).select_related('artist__artistprofile').order_by('-event_date')
    return render(request, 'dashboards/organizer_bookings.html', {'bookings': bookings})


@login_required
def organizer_upcoming_events_view(request):
    """Displays only future ACCEPTED bookings for the organizer."""
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    # FIX: The query now correctly filters on the User instance 'request.user'.
    upcoming_bookings = Booking.objects.filter(
        organizer=request.user,
        status='ACCEPTED',
        event_date__gte=timezone.now().date()
    ).select_related('artist__artistprofile').order_by('event_date')
    return render(request, 'dashboards/organizer_upcoming_events.html', {'upcoming_bookings': upcoming_bookings})


@login_required
def booking_success_view(request, booking_id):
    """Confirmation message after a booking request has been sent."""
    # FIX: The lookup is now 'organizer=request.user', not 'organizer__user'.
    booking = get_object_or_404(Booking, pk=booking_id, organizer=request.user)
    return render(request, 'bookings/booking_success.html', {'booking': booking})


from django.utils import timezone
from datetime import date

@login_required
def create_booking_view(request, artist_id):
    """Handles booking request creation by organizer."""
    artist_profile = get_object_or_404(ArtistProfile, pk=artist_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            event_date = form.cleaned_data['event_date']

            # ✅ Prevent past dates
            if event_date and event_date < date.today():
                messages.error(request, "You cannot book for a past date. Please choose a future date.")
                return redirect('create_booking', artist_id=artist_id)

            # ✅ Check artist availability
            if Availability.objects.filter(artist=artist_profile, date=event_date).exists():
                messages.error(request, f"{artist_profile.contact_name} is not available on that date.")
                return redirect('create_booking', artist_id=artist_id)

            booking = form.save(commit=False)
            booking.organizer = request.user
            booking.artist = artist_profile.user
            booking.status = 'PENDING'
            booking.save()

            return redirect('booking_success', booking_id=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'artist': artist_profile
    })


# --- ARTIST VIEWS (ALL QUERIES CORRECTED) ---

@login_required
def artist_booking_requests_view(request):
    """Displays booking requests for the logged-in artist."""
    if request.user.role != 'ARTIST':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    # FIX: This query was already correct, verified to remain.
    bookings = Booking.objects.filter(artist=request.user).select_related('organizer__organizerprofile').order_by('-created_at')
    return render(request, 'dashboards/artist_booking_requests.html', {'bookings': bookings})


@login_required
def respond_to_booking_view(request, booking_id, action):
    """Allows an artist to accept or decline a booking request."""
    booking = get_object_or_404(Booking, pk=booking_id, artist=request.user)
    artist_profile = get_object_or_404(ArtistProfile, user=request.user)

    if booking.status == 'PENDING':
        if action == 'accept':
            booking.status = 'ACCEPTED'
            Availability.objects.create(
                artist=artist_profile,
                date=booking.event_date,
                is_booked=True,
            )
            messages.success(request, "Booking accepted! The date has been blocked on your calendar.")
        elif action == 'decline':
            booking.status = 'DECLINED'
            messages.info(request, "Booking has been declined.")
        booking.save()
    else:
        messages.error(request, "This booking has already been responded to.")

    return redirect('artist_booking_requests')


# --- NOTIFICATIONS (ALL QUERIES CORRECTED) ---

@login_required
def notifications_view(request):
    """Displays and marks notifications as read."""
    # FIX: The Notification model's field is 'recipient', not 'user'.
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'bookings/notifications.html', {'notifications': notifications})

@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "bookings/booking_detail.html", {"booking": booking})
