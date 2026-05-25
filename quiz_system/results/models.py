from django.db import models
from users.models import User
from exams.models import Exam
from questions.models import Question

class ExamAttempt(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='attempts'
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE, 
        related_name='attempts'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    def percentage(self):
        if self.total_marks > 0:
            return round((self.score / self.total_marks) * 100, 2)
        return 0

class Answer(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE
    )
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.student.username} - Q{self.question.id}"