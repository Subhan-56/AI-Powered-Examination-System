from django.db import models
from users.models import User

class Exam(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_exams'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    total_marks = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    assigned_students = models.ManyToManyField(
        User, 
        related_name='assigned_exams', 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_always_active = models.BooleanField(default=False) 

    def __str__(self):
        return self.title

    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'published'

    def total_questions(self):
        return self.questions.filter(is_approved=True).count()