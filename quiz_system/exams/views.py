from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from .models import Exam
from questions.models import Question
from users.models import User

# ============================================================
# TEACHER — Create Exam
# ============================================================
@login_required
def create_exam(request):
    if not request.user.is_teacher():
        messages.error(request, 'Access denied!')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = request.POST.get('duration_minutes')
        timing_type = request.POST.get('timing_type', 'scheduled')

        from django.utils import timezone
        import datetime

        if timing_type == 'anytime':
            # Hamesha active rahega
            start_time = timezone.now() - datetime.timedelta(days=1)
            end_time = timezone.now() + datetime.timedelta(days=365)
            is_always_active = True
        else:
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            is_always_active = False

        exam = Exam.objects.create(
            title=title,
            description=description,
            teacher=request.user,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            is_always_active=is_always_active,
            status='draft'
        )
        messages.success(request, f'Exam "{title}" created! Now add questions.')
        return redirect('add_question', exam_id=exam.id)

    return render(request, 'exams/create_exam.html')



# ============================================================
# TEACHER — Add Question
# ============================================================
@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    questions = Question.objects.filter(exam=exam)

    if request.method == 'POST':
        text = request.POST.get('text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        marks = request.POST.get('marks', 1)
        topic = request.POST.get('topic', '')

        Question.objects.create(
            exam=exam,
            text=text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            marks=marks,
            topic=topic,
            is_ai_generated=False,
            is_approved=True
        )

        # Update total marks
        exam.total_marks = sum(q.marks for q in exam.questions.all())
        exam.save()

        messages.success(request, 'Question added!')
        return redirect('add_question', exam_id=exam.id)

    return render(request, 'exams/add_question.html', {
        'exam': exam,
        'questions': questions
    })


# ============================================================
# TEACHER — Publish Exam & Assign Students
# ============================================================
@login_required
def publish_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    students = User.objects.filter(role='student')

    if request.method == 'POST':
        selected_students = request.POST.getlist('students')
        exam.assigned_students.set(selected_students)
        exam.status = 'published'
        exam.save()

        # Notification bhejo
        try:
            from notifications.utils import send_exam_assigned_notification
            from users.models import User as UserModel
            assigned = UserModel.objects.filter(id__in=selected_students)
            send_exam_assigned_notification(exam, assigned)
        except Exception:
            pass

        messages.success(request, f'Exam "{exam.title}" published successfully!')
        return redirect('teacher_dashboard')

    return render(request, 'exams/publish_exam.html', {
        'exam': exam,
        'students': students
    })


# ============================================================
# TEACHER — My Exams List
# ============================================================
@login_required
def my_exams(request):
    exams = Exam.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'exams/my_exams.html', {'exams': exams})


# ============================================================
# TEACHER — Delete Question
# ============================================================
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id
    question.delete()
    messages.success(request, 'Question deleted!')
    return redirect('add_question', exam_id=exam_id)



@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

    if request.method == 'POST':
        exam.title = request.POST.get('title')
        exam.description = request.POST.get('description')
        exam.duration_minutes = request.POST.get('duration_minutes')
        timing_type = request.POST.get('timing_type', 'scheduled')

        if timing_type == 'anytime':
            exam.start_time = timezone.now() - datetime.timedelta(days=1)
            exam.end_time = timezone.now() + datetime.timedelta(days=365)
            exam.is_always_active = True
        else:
            exam.start_time = request.POST.get('start_time')
            exam.end_time = request.POST.get('end_time')
            exam.is_always_active = False

        exam.save()
        messages.success(request, 'Exam updated successfully!')
        return redirect('my_exams')

    return render(request, 'exams/edit_exam.html', {'exam': exam})


@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    title = exam.title
    exam.delete()
    messages.success(request, f'Exam "{title}" deleted!')
    return redirect('my_exams')