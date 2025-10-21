from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Conversation, Message
from accounts.models import ArtistProfile

@login_required
def inbox_view(request):
    # Get all conversations the user is a part of
    conversations_qs = Conversation.objects.filter(
        Q(artist__user=request.user) | Q(organizer__user=request.user)
    ).order_by('-created_at')

    # Create a new list to hold conversation data + unread status
    conversations_with_status = []
    for conv in conversations_qs:
        unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        conversations_with_status.append({
            'conversation': conv,
            'has_unread': unread_count > 0
        })

    return render(request, 'messaging/inbox.html', {'conversations_with_status': conversations_with_status})

@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    # Security check...
    if request.user != conversation.artist.user and request.user != conversation.organizer.user:
        return redirect('inbox')

    # --- ADD THIS LINE TO MARK MESSAGES AS READ ---
    # Mark messages sent by the OTHER person in this conversation as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)


    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
        return redirect('conversation', conversation_id=conversation_id)
        
    messages = conversation.messages.all().order_by('timestamp')
    return render(request, 'messaging/conversation.html', {'conversation': conversation, 'messages': messages})

@login_required
def start_conversation_view(request, artist_id):
    if request.user.role != 'ORGANIZER':
        return redirect('artist_profile', artist_id=artist_id)
        
    artist = get_object_or_404(ArtistProfile, pk=artist_id)
    organizer = request.user.organizerprofile
    
    conversation, created = Conversation.objects.get_or_create(artist=artist, organizer=organizer)
    return redirect('conversation', conversation_id=conversation.pk)
