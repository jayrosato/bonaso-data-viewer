from .models import Message

def unread_message_notice(request):
    if request.user.is_authenticated:
        unread = Message.objects.filter(recipient=request.user, read=False).exists()
        return {'has_unread_messages': unread}
    return {}
        