from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('mark-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:notif_id>/delete/', views.delete_notification, name='delete_notification'),
]

