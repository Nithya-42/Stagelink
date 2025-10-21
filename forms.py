from django import forms
from django.forms import formset_factory
from .models import ArtistProfile, OrganizerProfile, PortfolioItem, GroupMember

class ArtistSignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text='This will be your login email.')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = ArtistProfile
        # Use the correct 'contact_name' field
        fields = ['contact_name', 'phone', 'category', 'location', 'pricing_per_event', 'profile_photo', 'government_id']


class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['name', 'role', 'photo']

# This is the main registration form for the group/band
class GroupSignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = ArtistProfile
        fields = [
            'group_name', 'contact_name', 'phone', 'category', 'location', 
            'pricing_per_event', 'profile_photo', 'government_id'
        ]
        labels = {
            'group_name': "Band / Group Name",
            'contact_name': "Group Leader / Manager's Name",
            'profile_photo': "Group Logo or Main Photo"
        }

# This creates a factory that can generate multiple GroupMemberForm instances
GroupMemberFormSet = formset_factory(GroupMemberForm, extra=1)


class OrganizerSignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text='This will be your login email.')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = OrganizerProfile
        fields = ['full_name', 'organization_name', 'phone']


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = ['contact_name', 'group_name', 'phone', 'category', 'location', 'pricing_per_event', 'bio', 'profile_photo']


class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ['full_name', 'organization_name', 'phone']


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'file_type', 'file', 'url']


class AvailabilityForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

