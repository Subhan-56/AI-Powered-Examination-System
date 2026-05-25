from django.db import models
from users.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('exam_assigned', 'Exam Assigned'),
        ('result_ready', 'Result Ready'),
        ('ai_generated', 'AI Questions Generated'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='general'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
    