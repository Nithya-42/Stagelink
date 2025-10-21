from django.urls import path
from . import views

urlpatterns = [
    # --- ORGANIZER-FACING URLS ---
    path('create/<int:artist_id>/', views.create_booking_view, name='create_booking'),
    path('success/<int:booking_id>/', views.booking_success_view, name='booking_success'),
    path('booking/<int:pk>/', views.booking_detail_view, name='booking_detail'),
    
    
    # These URLs are now handled by the 'accounts' app and should not be here.
    # The links on your dashboard already point to the correct views in accounts/.
    # path('my-bookings/', views.organizer_bookings_view, name='organizer_bookings'),
    # path('upcoming-events/', views.organizer_upcoming_events_view, name='organizer_upcoming_events'),

    # --- ARTIST-FACING URLS ---
    # FIX: Corrected the name from 'artist_booking_requestsS'
    path('requests/', views.artist_booking_requests_view, name='artist_booking_requests'),
    
    # FIX: This single, correct path replaces the old 'accept' and 'reject' paths.
    path('respond/<int:booking_id>/<str:action>/', views.respond_to_booking_view, name='respond_to_booking'),

    # --- NOTIFICATIONS URL ---
    path('notifications/', views.notifications_view, name='notifications'),
]

