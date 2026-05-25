from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Sab read mark karo jab page khule
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_all_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    return redirect('notifications_list')


@login_required
def delete_notification(request, notif_id):
    notif = get_object_or_404(
        Notification,
        id=notif_id,
        user=request.user
    )
    notif.delete()
    return redirect('notifications_list')

