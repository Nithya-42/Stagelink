from django.db import models
from django.conf import settings

class Conversation(models.Model):
    artist = models.ForeignKey('accounts.ArtistProfile', on_delete=models.CASCADE, related_name='conversations')
    organizer = models.ForeignKey('accounts.OrganizerProfile', on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('artist', 'organizer')

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)