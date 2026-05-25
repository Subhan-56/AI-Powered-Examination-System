from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from exams.models import Exam
from questions.models import Question
from .models import ExamAttempt, Answer

# ============================================================
# STUDENT — Available Exams List
# ============================================================
@login_required
def available_exams(request):
    if not request.user.is_student():
        messages.error(request, 'Access denied!')
        return redirect('student_dashboard')

    exams = Exam.objects.filter(
        assigned_students=request.user,
        status='published'
    ).order_by('start_time')

    exam_data = []
    for exam in exams:
        attempt = ExamAttempt.objects.filter(
            student=request.user,
            exam=exam,
            is_submitted=True
        ).first()

        now = timezone.now()

        # is_always_active wale exams hamesha active hain
        if exam.is_always_active:
            is_active = True
            is_upcoming = False
            is_expired = False
        else:
            is_active = exam.start_time <= now <= exam.end_time
            is_upcoming = now < exam.start_time
            is_expired = now > exam.end_time

        exam_data.append({
            'exam': exam,
            'attempted': attempt is not None,
            'attempt': attempt,
            'is_active': is_active,
            'is_upcoming': is_upcoming,
            'is_expired': is_expired,
        })

    return render(request, 'results/available_exams.html', {
        'exam_data': exam_data
    })


# ============================================================
# STUDENT — Start Exam
# ============================================================
@login_required
def start_exam(request, exam_id):
    if not request.user.is_student():
        return redirect('student_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, status='published')
    now = timezone.now()

    # Time check — is_always_active wale skip karein
    if not exam.is_always_active:
        if now < exam.start_time:
            messages.error(request, 'Exam has not started yet!')
            return redirect('available_exams')

        if now > exam.end_time:
            messages.error(request, 'Exam time has expired!')
            return redirect('available_exams')

    # Already attempt kiya?
    existing = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam,
        is_submitted=True
    ).first()

    if existing:
        messages.warning(request, 'You have already attempted this exam!')
        return redirect('view_result', attempt_id=existing.id)

    # Attempt banao ya existing lo
    attempt, created = ExamAttempt.objects.get_or_create(
        student=request.user,
        exam=exam,
        is_submitted=False,
        defaults={'total_marks': exam.total_marks}
    )

    questions = Question.objects.filter(
        exam=exam,
        is_approved=True
    )

    # Duration ke mutabiq timer set karo
    exam_end = attempt.started_at + datetime.timedelta(
        minutes=exam.duration_minutes
    )

    # Agar scheduled hai toh exam end time bhi check karo
    if not exam.is_always_active:
        exam_end = min(exam_end, exam.end_time)

    end_time_timestamp = int(exam_end.timestamp() * 1000)

    return render(request, 'results/attempt_exam.html', {
        'exam': exam,
        'questions': questions,
        'attempt': attempt,
        'end_time_timestamp': end_time_timestamp,
    })


# ============================================================
# STUDENT — Submit Exam & Auto Evaluate
# ============================================================
@login_required
def submit_exam(request, attempt_id):
    if request.method != 'POST':
        return redirect('available_exams')

    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user,
        is_submitted=False
    )

    exam = attempt.exam
    questions = Question.objects.filter(exam=exam, is_approved=True)

    correct_count = 0
    total_marks = 0

    for question in questions:
        selected = request.POST.get(f'question_{question.id}', '')
        is_correct = selected == question.correct_answer

        if is_correct:
            correct_count += question.marks

        total_marks += question.marks

        Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_option': selected,
                'is_correct': is_correct
            }
        )

    # Score save karo
    attempt.score = correct_count
    attempt.total_marks = total_marks
    attempt.is_submitted = True
    attempt.submitted_at = timezone.now()
    attempt.time_taken = int(
        (timezone.now() - attempt.started_at).total_seconds()
    )
    attempt.save()

    # Result notification bhejo
    try:
        from notifications.utils import send_result_notification
        send_result_notification(attempt)
    except Exception:
        pass

    messages.success(request, 'Exam submitted! Here are your results.')
    return redirect('view_result', attempt_id=attempt.id)


# ============================================================
# STUDENT — View Result
# ============================================================
@login_required
def view_result(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )

    answers = Answer.objects.filter(
        attempt=attempt
    ).select_related('question')

    # Grade calculate karo
    percentage = attempt.percentage()
    wrong = int(answers.count() - (attempt.score or 0))

    if percentage >= 90:
        grade = 'A+'
        grade_color = 'success'
        message = 'Excellent! Outstanding performance!'
    elif percentage >= 80:
        grade = 'A'
        grade_color = 'success'
        message = 'Great job! Well done!'
    elif percentage >= 70:
        grade = 'B'
        grade_color = 'info'
        message = 'Good work! Keep it up!'
    elif percentage >= 60:
        grade = 'C'
        grade_color = 'warning'
        message = 'Average performance. Try harder!'
    elif percentage >= 50:
        grade = 'D'
        grade_color = 'warning'
        message = 'Below average. More practice needed!'
    else:
        grade = 'F'
        grade_color = 'danger'
        message = 'Failed. Please revise and try again!'

    return render(request, 'results/view_result.html', {
        'attempt': attempt,
        'answers': answers,
        'percentage': percentage,
        'grade': grade,
        'grade_color': grade_color,
        'result_message': message,
        'wrong': wrong,
    })


# ============================================================
# TEACHER — View All Results of Exam
# ============================================================
@login_required
def exam_results(request, exam_id):
    if not request.user.is_teacher():
        return redirect('teacher_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        is_submitted=True
    ).select_related('student').order_by('-score')

    return render(request, 'results/exam_results.html', {
        'exam': exam,
        'attempts': attempts,
    })

