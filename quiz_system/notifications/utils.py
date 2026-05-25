from .models import Notification

def send_notification(user, title, message, notification_type='general'):
    """Helper function to send notification to a user"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )

def send_exam_assigned_notification(exam, students):
    """Exam assign hone pe students ko notify karo"""
    for student in students:
        send_notification(
            user=student,
            title=f'New Exam Assigned: {exam.title}',
            message=f'You have been assigned a new exam "{exam.title}". '
                   f'It starts on {exam.start_time.strftime("%B %d, %Y at %H:%M")}.',
            notification_type='exam_assigned'
        )

def send_result_notification(attempt):
    """Result ready hone pe student ko notify karo"""
    send_notification(
        user=attempt.student,
        title=f'Result Ready: {attempt.exam.title}',
        message=f'Your result for "{attempt.exam.title}" is ready. '
               f'You scored {attempt.score}/{attempt.total_marks}.',
        notification_type='result_ready'
    )

    