
# accounts/views.py

# --- 1. CLEANED UP IMPORTS ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib import messages
import calendar
from django.utils import timezone
from .forms import GroupMemberForm

# --- 2. CORRECT MODEL IMPORTS ---
from bookings.models import Booking
from reviews.models import Favorite, Review 

# --- 3. LOCAL MODEL & FORM IMPORTS ---
from .models import User, ArtistProfile, OrganizerProfile, PortfolioItem, Availability, GroupMember
from .forms import (
    ArtistSignUpForm, OrganizerSignUpForm, GroupSignUpForm, GroupMemberFormSet,
    ArtistProfileForm, OrganizerProfileForm, PortfolioItemForm, AvailabilityForm
)

# --- 4. ALL VIEWS (NO DUPLICATES) ---
def home_view(request):
    # ✅ Fetch only approved artists
    artists = ArtistProfile.objects.filter(is_approved=True)[:6]  # limit to 6 featured artists
    return render(request, 'core/home.html', {'artists': artists})

def signup_chooser(request):
    return render(request, 'registration/signup_chooser.html')

class ArtistSignUpView(CreateView):
    form_class = ArtistSignUpForm
    template_name = 'registration/signup_form.html'
    success_url = reverse_lazy('registration_pending')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Artist'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # Step 1: Create User
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            role=User.Role.ARTIST,
            is_active=False
        )

        # Step 2: Create ArtistProfile with remaining fields
        profile = form.save(commit=False)
        profile.user = user
        profile.save()

        return redirect(self.success_url)

class OrganizerSignUpView(CreateView):
    form_class = OrganizerSignUpForm
    template_name = 'registration/signup_form.html'
    success_url = reverse_lazy('account_login')

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Organizer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # Step 1: Create User
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            role=User.Role.ORGANIZER
        )

        # Step 2: Create OrganizerProfile
        profile = form.save(commit=False)
        profile.user = user
        profile.save()

        messages.success(self.request, "Registration successful! Please log in.")
        return redirect(self.success_url)


def registration_pending_view(request):
    return render(request, 'account/account_inactive.html')
class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if self.request.user.role == 'ARTIST':
            return ['dashboards/artist_dashboard.html']
        elif self.request.user.role == 'ORGANIZER':
            return ['dashboards/organizer_dashboard.html']
        return ['core/home.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == 'ARTIST':
            profile = get_object_or_404(ArtistProfile, user=user)
            context['completion_percentage'] = profile.calculate_completion_percentage()

        elif user.role == 'ORGANIZER':
            profile = get_object_or_404(OrganizerProfile, user=user)
            now = timezone.now()
            
            # All queries are now definitively correct
            upcoming_bookings = Booking.objects.filter(organizer=user, status='ACCEPTED', event_date__gte=now).order_by('event_date')
            favorite_artists_count = Favorite.objects.filter(organizer=user).count()
            past_bookings_pending_review = Booking.objects.filter(organizer=user, status='ACCEPTED', event_date__lt=now).exclude(review__organizer=user).order_by('-event_date')
            
            context['completion_percentage'] = profile.calculate_completion_percentage()
            context['upcoming_events_count'] = upcoming_bookings.count()
            context['next_upcoming_event'] = upcoming_bookings.first()
            context['favorite_artists_count'] = favorite_artists_count
            context['past_events_pending_review_count'] = past_bookings_pending_review.count()
            context['latest_past_event_for_review'] = past_bookings_pending_review.first()
            
        return context

# --- 4. ORGANIZER-SPECIFIC VIEWS (AUDITED AND CORRECT) ---

@login_required
def favorite_artists_view(request):
    favorites = Favorite.objects.filter(organizer=request.user).select_related('artist__artistprofile')
    favorite_artists = [fav.artist for fav in favorites]
    context = {'favorite_artists': favorite_artists}
    return render(request, 'dashboards/favorite_artists.html', context)

@login_required
def organizer_past_events_view(request):
    now = timezone.now()
    past_bookings = Booking.objects.filter(organizer=request.user, status='ACCEPTED', event_date__lt=now).select_related('artist__artistprofile').order_by('-event_date')
    reviewed_booking_ids = Review.objects.filter(organizer=request.user).values_list('booking_id', flat=True)
    context = {'past_bookings': past_bookings, 'reviewed_booking_ids': set(reviewed_booking_ids)}
    return render(request, 'dashboards/organizer_past_events.html', context)



# --- Other required views ---
def artist_list_view(request):
    CATEGORIES = ['Singer', 'Band', 'DJ', 'Musician (Instrumental)', 'Comedian', 'Dancer (Solo)', 'Dance Group', 'Magician', 'Host/MC', 'Speaker']
    LOCATIONS = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Kochi', 'Goa']
    artists = ArtistProfile.objects.filter(is_approved=True)
    category_filter = request.GET.get('category')
    location_filter = request.GET.get('location')
    if category_filter:
        artists = artists.filter(category__iexact=category_filter)
    if location_filter:
        artists = artists.filter(location__iexact=location_filter)
    context = {'artists': artists, 'categories': CATEGORIES, 'locations': LOCATIONS, 'selected_category': category_filter, 'selected_location': location_filter}
    return render(request, 'accounts/browse_artists.html', context)
    


# --- 4. THE CORRECTED ARTIST PROFILE VIEW ---

def artist_profile_view(request, artist_id):
    """Displays the public profile for a single artist or group."""
    artist_profile = get_object_or_404(ArtistProfile, pk=artist_id, is_approved=True)

    # Fetch reviews
    reviews = Review.objects.filter(artist=artist_profile.user).order_by('-created_at')

    # Fetch unavailable dates
    unavailable_dates = list(
        Availability.objects.filter(artist=artist_profile).values_list('date', flat=True)
    )

    today = timezone.now().date()
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(today.year, today.month)

    # ✅ Add group members if this is a group
    group_members = None
    if artist_profile.is_group:
        group_members = artist_profile.members.all()

    context = {
        'artist': artist_profile,
        'reviews': reviews,
        'unavailable_dates': unavailable_dates,
        'month_days': month_days,
        'current_month_name': calendar.month_name[today.month],
        'group_members': group_members,  # <-- added
    }
    return render(request, 'accounts/artist_profile.html', context)


class EditArtistProfileView(LoginRequiredMixin, UpdateView):
    model = ArtistProfile
    form_class = ArtistProfileForm
    template_name = 'dashboards/edit_artist_profile.html'
    success_url = reverse_lazy('dashboard')
    def get_object(self):
        return self.request.user.artistprofile

class EditOrganizerProfileView(LoginRequiredMixin, UpdateView):
    model = OrganizerProfile
    form_class = OrganizerProfileForm
    template_name = 'dashboards/edit_organizer_profile.html'
    success_url = reverse_lazy('dashboard')
    def get_object(self):
        return self.request.user.organizerprofile
    
class GroupSignUpView(CreateView):
    form_class = GroupSignUpForm
    template_name = 'registration/group_signup_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['member_formset'] = GroupMemberFormSet(self.request.POST)
        else:
            context['member_formset'] = GroupMemberFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        member_formset = context['member_formset']

        if member_formset.is_valid():
            # Step 1: Create User
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                role=User.Role.ARTIST,
                is_active=False
            )

            # Step 2: Create ArtistProfile for the group
            profile = form.save(commit=False)
            profile.user = user
            profile.is_group = True
            profile.save()

            # Step 3: Save group members
            for member_form in member_formset:
                if member_form.cleaned_data:
                    member = member_form.save(commit=False)
                    member.group = profile
                    member.save()

            return redirect('account_inactive')
        else:
            return self.form_invalid(form)


# --- Other views like  Manage Portfolio, etc. should follow ---
# Make sure you have one and only one definition for each view.

@login_required
def my_profile_view(request):
    """
    Displays the correct profile view page based on the user's role.
    """
    if request.user.role == 'ARTIST':
        template_name = 'dashboards/view_artist_profile.html'
        profile = get_object_or_404(ArtistProfile, user=request.user)
        # For groups, also get the members
        group_members = None
        if profile.is_group:
            group_members = profile.members.all()

        
        context = {'profile': profile, 'group_members': group_members}

    elif request.user.role == 'ORGANIZER':
        template_name = 'dashboards/view_organizer_profile.html'
        profile = get_object_or_404(OrganizerProfile, user=request.user)
        context = {'profile': profile}
        
    else:
        # Fallback for superusers or other unexpected roles
        return redirect('admin:index')

    return render(request, template_name, context)


@login_required
def organizer_upcoming_events_view(request):
    upcoming_bookings = Booking.objects.filter(
        organizer=request.user,
        status='ACCEPTED',
        event_date__gte=timezone.now()
    ).select_related('artist__artistprofile').order_by('event_date')
    context = {'upcoming_bookings': upcoming_bookings}
    return render(request, 'dashboards/organizer_upcoming_events.html', context)


@login_required
def manage_portfolio_view(request):
    artist_profile = request.user.artistprofile
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio_item = form.save(commit=False)
            portfolio_item.artist = artist_profile
            portfolio_item.save()
            return redirect('manage_portfolio')
    else:
        form = PortfolioItemForm()
    portfolio_items = PortfolioItem.objects.filter(artist=artist_profile)
    context = {'form': form, 'portfolio_items': portfolio_items}
    return render(request, 'dashboards/manage_portfolio.html', context)

@login_required
def manage_availability_view(request):
    artist_profile = request.user.artistprofile
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            availability, created = Availability.objects.get_or_create(artist=artist_profile, date=date, defaults={'is_booked': True})
            if created:
                messages.success(request, f'Date {date} has been blocked out on your calendar.')
            else:
                messages.warning(request, f'Date {date} was already blocked out.')
            return redirect('manage_availability')
    else:
        form = AvailabilityForm()
    blocked_dates = Availability.objects.filter(artist=artist_profile).order_by('date')
    context = {'form': form, 'blocked_dates': blocked_dates}
    return render(request, 'dashboards/manage_availability.html', context)

@login_required
def delete_availability_view(request, pk):
    availability = get_object_or_404(Availability, pk=pk, artist=request.user.artistprofile)
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Date removed from your availability.')
        return redirect('manage_availability')
    return redirect('manage_availability')

@login_required
def profile_view_redirect(request):
    if request.user.role == 'ARTIST':
        return redirect('edit_artist_profile')
    elif request.user.role == 'ORGANIZER':
        return redirect('edit_organizer_profile')
    else:
        return redirect('admin:index')



@login_required
def artist_reviews_view(request):
    """
    Displays a list of all reviews left for an artist.
    """
    artist_profile = get_object_or_404(ArtistProfile, user=request.user)

    # Get all reviews for this artist
    reviews = Review.objects.filter(artist=request.user).order_by('-created_at')

    context = {
        'reviews': reviews,
    }
    return render(request, 'dashboards/artist_reviews.html', context)

@login_required
def organizer_bookings_view(request):
    all_bookings = Booking.objects.filter(
        organizer=request.user
    ).select_related('artist__artistprofile').order_by('-event_date')
    context = {'bookings': all_bookings}
    return render(request, 'dashboards/organizer_bookings.html', context)

@login_required
def artist_booking_requests_view(request):
    """
    Displays booking requests for the logged-in artist.
    This query is audited and correct.
    """
    bookings = Booking.objects.filter(artist=request.user).select_related('organizer__organizerprofile').order_by('-created_at')
    context = {'bookings': bookings}
    return render(request, 'dashboards/artist_booking_requests.html', context)

# --- THIS IS THE NEW, REQUIRED VIEW ---
@login_required
def booking_detail_view(request, booking_id):
    """
    Displays the details of a single booking.
    Accessible by either the artist or the organizer involved.
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Security check to ensure only the artist or organizer can view it
    if request.user != booking.artist and request.user != booking.organizer:
        messages.error(request, "You do not have permission to view this booking.")
        return redirect('dashboard')

    context = {'booking': booking}
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def toggle_favorite(request, artist_id):
    artist = get_object_or_404(ArtistProfile, pk=artist_id)
    organizer_profile = get_object_or_404(OrganizerProfile, user=request.user)

    if artist in organizer_profile.favorite_artists.all():
        organizer_profile.favorite_artists.remove(artist)
        messages.success(request, f"{artist.full_name} removed from favorites.")
    else:
        organizer_profile.favorite_artists.add(artist)
        messages.success(request, f"{artist.full_name} added to favorites.")

    return redirect(request.META.get("HTTP_REFERER", "discover_artists"))
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import GroupMember, ArtistProfile
from .forms import GroupMemberForm

@login_required
def manage_group_members(request):
    profile = get_object_or_404(ArtistProfile, user=request.user, is_group=True)
    members = profile.members.all()
    return render(request, 'dashboards/manage_group_members.html', {
        'profile': profile,
        'members': members
    })

@login_required
def add_group_member(request):
    profile = get_object_or_404(ArtistProfile, user=request.user, is_group=True)
    if request.method == "POST":
        form = GroupMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.group = profile
            member.save()
            return redirect('manage_group_members')
    else:
        form = GroupMemberForm()
    return render(request, 'dashboards/add_group_member.html', {'form': form})

@login_required
def edit_group_member(request, member_id):
    profile = get_object_or_404(ArtistProfile, user=request.user, is_group=True)
    member = get_object_or_404(GroupMember, id=member_id, group=profile)
    if request.method == "POST":
        form = GroupMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('manage_group_members')
    else:
        form = GroupMemberForm(instance=member)
    return render(request, 'dashboards/edit_group_member.html', {'form': form, 'member': member})

@login_required
def delete_group_member(request, member_id):
    profile = get_object_or_404(ArtistProfile, user=request.user, is_group=True)
    member = get_object_or_404(GroupMember, id=member_id, group=profile)
    if request.method == "POST":
        member.delete()
        return redirect('manage_group_members')
    return render(request, 'dashboards/delete_group_member.html', {'member': member})
