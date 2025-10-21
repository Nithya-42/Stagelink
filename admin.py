from django.contrib import admin
from .models import User, ArtistProfile, OrganizerProfile, PortfolioItem, Availability, GroupMember
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

# Action function to approve artists
def approve_artists(modeladmin, request, queryset):
    for artist_profile in queryset:
        artist_profile.is_approved = True
        artist_profile.user.is_active = True
        artist_profile.user.save()
        artist_profile.save()
        # Check preference before sending email
        if artist_profile.user.email_notifications_enabled:
            subject = 'Your StageLink Account has been Approved!'
            login_url = request.build_absolute_uri(reverse('account_login'))
            context = {'artist': artist_profile, 'login_url': login_url}
            message = render_to_string('emails/artist_approval_email.html', context)
            send_mail(subject, message, 'donotreply@stagelink.com', [artist_profile.user.email], html_message=message)
approve_artists.short_description = "Approve selected artists"

# Inline admin for group members
class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1

# Main Admin class for Artist Profiles
class ArtistProfileAdmin(admin.ModelAdmin):
    # Use the CORRECT field name 'contact_name'
    list_display = ('__str__', 'contact_name', 'category', 'location', 'is_group', 'is_approved')
    list_filter = ('is_approved', 'is_group', 'category')
    search_fields = ('contact_name', 'group_name', 'user__email')
    actions = [approve_artists]
    inlines = [GroupMemberInline]

# Register your models
admin.site.register(User)
admin.site.register(ArtistProfile, ArtistProfileAdmin)
admin.site.register(OrganizerProfile)
admin.site.register(PortfolioItem)
admin.site.register(Availability)

