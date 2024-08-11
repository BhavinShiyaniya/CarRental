from car.models import Notification

def get_notification(request):
    # notification
    notifications = Notification.objects.filter(owner=request.user.id).filter(is_read=False)
    return {'notifications': notifications, 'notifications_count': notifications.count()}