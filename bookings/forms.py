from django import forms
from .models import Booking
from django.utils import timezone
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event_date', 'event_details']
        widgets = {
            'event_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().date().strftime('%Y-%m-%d')  # blocks past dates in UI
                }
            ),
            'event_details': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Describe the event, location, time, and your requirements.'
                }
            ),
        }

    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < timezone.now().date():
            raise ValidationError("You cannot book an event for a past date.")
        return event_date
