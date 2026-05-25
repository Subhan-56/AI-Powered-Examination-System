from django.db import models
from exams.models import Exam

class Question(models.Model):
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )
    marks = models.IntegerField(default=1)
    topic = models.CharField(max_length=100, blank=True)
    is_ai_generated = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
