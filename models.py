from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        ARTIST = "ARTIST", "Artist"
        ORGANIZER = "ORGANIZER", "Organizer"
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices)
    email_notifications_enabled = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='artistprofile')
    is_group = models.BooleanField(default=False)
    group_name = models.CharField(max_length=255, blank=True, null=True, help_text="The name of the band or group.")
    contact_name = models.CharField(max_length=255, verbose_name="Full Name (for contact)")
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    pricing_per_event = models.DecimalField(max_digits=10, decimal_places=2)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, help_text="Main photo for an individual or a group logo.")
    government_id = models.FileField(upload_to='gov_ids/')
    is_approved = models.BooleanField(default=False)

    def calculate_completion_percentage(self):
        total_fields = 7
        filled_fields = 0
        if self.contact_name:
            filled_fields += 1
        if self.phone:
            filled_fields += 1
        if self.category:
            filled_fields += 1
        if self.location:
            filled_fields += 1
        if self.pricing_per_event is not None:
            filled_fields += 1
        if self.bio:
            filled_fields += 1
        if self.profile_photo:
            filled_fields += 1
        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0

    def __str__(self):
        return self.group_name if self.is_group and self.group_name else self.contact_name

class GroupMember(models.Model):
    group = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, help_text="e.g., Vocalist, Guitarist, Lead Dancer")
    photo = models.ImageField(upload_to='group_members/', blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.role}) - {self.group.group_name}'

class OrganizerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='organizerprofile')
    full_name = models.CharField(max_length=255)
    organization_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    def get_favorite_artists(self):
        return [favorite.artist for favorite in self.favorites.all()]

    def calculate_completion_percentage(self):
        total_fields = 3
        filled_fields = 0
        if self.full_name:
            filled_fields += 1
        if self.organization_name:
            filled_fields += 1
        if self.phone:
            filled_fields += 1
        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0

    def __str__(self):
        return self.full_name

class PortfolioItem(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='portfolio')
    file_type = models.CharField(max_length=10, choices=models.TextChoices('FileType', 'IMAGE VIDEO AUDIO').choices)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='portfolio_files/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    def __str__(self):
        return f"{self.title} for {self.artist}"

class Availability(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'Availabilities'
    def __str__(self):
        return f"{self.artist} - {self.date}"

