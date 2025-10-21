# reviews/admin.py
from django.contrib import admin
from .models import Review, Favorite

admin.site.register(Review)
admin.site.register(Favorite)