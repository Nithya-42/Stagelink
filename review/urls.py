from django.urls import path
from . import views

urlpatterns = [
    # This file should ONLY contain URLs related to the reviews app itself.
    path('add/<int:booking_id>/', views.add_review_view, name='add_review'),
    path('toggle-favorite/<int:artist_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    
    # The incorrect path for 'favorites/' that was causing the crash has been
    # PERMANENTLY REMOVED from this file.
]

