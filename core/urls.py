# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]