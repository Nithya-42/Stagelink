from django.shortcuts import render
from accounts.models import ArtistProfile

def home(request):
    """
    Renders the homepage.
    Fetches featured artists and a list of categories to display.
    """
    # Get up to 3 randomly ordered, approved artists to feature on the homepage.
    # Note: order_by('?') can be resource-intensive on large databases, but is fine for most projects.
    featured_artists = ArtistProfile.objects.filter(is_approved=True).order_by('?')[:3]
    
    # Get a distinct list of up to 5 categories from approved artists.
    # This ensures the categories shown are relevant to the available talent.
    categories = ArtistProfile.objects.filter(is_approved=True).values_list('category', flat=True).distinct()[:5]
    
    # Create the context dictionary to pass data to the template.
    context = {
        'featured_artists': featured_artists,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)

def about_us(request):
    """
    Renders the static 'About Us' page.
    """
    return render(request, 'core/about.html')

def how_it_works(request):
    """
    Renders the static 'How It Works' page.
    """
    return render(request, 'core/how_it_works.html')

def contact_us(request):
    """
    Renders the static 'Contact Us' page.
    """
    return render(request, 'core/contact.html')

def faq(request):
    """
    Renders the static 'FAQ' page.
    """
    return render(request, 'core/faq.html')

def terms_of_service(request):
    """
    Renders the static 'Terms of Service' page.
    """
    return render(request, 'core/terms.html')

def privacy_policy(request):
    """
    Renders the static 'Privacy Policy' page.
    """
    return render(request, 'core/privacy.html')
