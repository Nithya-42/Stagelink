from django.urls import path
from . import views


urlpatterns = [
    # --- AUTHENTICATION & REGISTRATION ---
    path('signup/', views.signup_chooser, name='signup_chooser'),
    path('signup/artist/', views.ArtistSignUpView.as_view(), name='artist_signup'),
    path('signup/organizer/', views.OrganizerSignUpView.as_view(), name='organizer_signup'),
    path('signup/group/', views.GroupSignUpView.as_view(), name='group_signup'), 
    path('registration-pending/', views.registration_pending_view, name='registration_pending'),

    # --- MAIN DASHBOARD ---
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # --- PUBLIC FACING ---
    path('artists/', views.artist_list_view, name='artist_list'),

    # --- PROFILE MANAGEMENT ---
    path('profile/edit/artist/', views.EditArtistProfileView.as_view(), name='edit_artist_profile'),
    path('profile/edit/organizer/', views.EditOrganizerProfileView.as_view(), name='edit_organizer_profile'),
    path('profile/my-profile/', views.my_profile_view, name='my_profile'),

    # --- ARTIST-SPECIFIC PAGES ---
    path('portfolio/manage/', views.manage_portfolio_view, name='manage_portfolio'),
    path('availability/manage/', views.manage_availability_view, name='manage_availability'),
    path('availability/delete/<int:pk>/', views.delete_availability_view, name='delete_availability'),
    path('booking-requests/', views.artist_booking_requests_view, name='artist_booking_requests'),
    path('my-reviews/', views.artist_reviews_view, name='artist_reviews'),
    
    # --- ORGANIZER-SPECIFIC PAGES ---
    
    path("favorites/", views.favorite_artists_view, name="favorite_artists"),
    path("toggle-favorite/<int:artist_id>/", views.toggle_favorite, name="toggle_favorite"),
    path('upcoming-events/', views.organizer_upcoming_events_view, name='organizer_upcoming_events'),
    path('past-events/', views.organizer_past_events_view, name='organizer_past_events'),
    path('my-bookings/', views.organizer_bookings_view, name='organizer_bookings'),
    path("artists/<int:artist_id>/", views.artist_profile_view, name="artist_profile"),
    
    path('group/members/', views.manage_group_members, name='manage_group_members'),
    path('group/members/add/', views.add_group_member, name='add_group_member'),
    path('group/members/<int:member_id>/edit/', views.edit_group_member, name='edit_group_member'),
    path('group/members/<int:member_id>/delete/', views.delete_group_member, name='delete_group_member'),
    


    

]

