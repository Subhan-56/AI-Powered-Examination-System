from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import RegisterForm

# ============================================================
# LOGIN VIEW
# ============================================================
def login_view(request):
    # Agar already logged in hai toh dashboard pe bhejo
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect_to_dashboard(user)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'users/login.html')


# ============================================================
# REGISTER VIEW
# ============================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')

        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'users/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return render(request, 'users/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'users/register.html')

        # Create user with proper password hashing
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.save()

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')

    return render(request, 'users/register.html')

# ============================================================
# LOGOUT VIEW
# ============================================================
def logout_view(request):
    logout(request)
    return redirect('login')


# ============================================================
# DASHBOARDS
# ============================================================
@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect_to_dashboard(request.user)
    return render(request, 'users/student_dashboard.html')


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return redirect_to_dashboard(request.user)
    return render(request, 'users/teacher_dashboard.html')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return redirect_to_dashboard(request.user)

    from exams.models import Exam
    from results.models import ExamAttempt

    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_exams = Exam.objects.count()
    total_attempts = ExamAttempt.objects.filter(is_submitted=True).count()

    recent_students = User.objects.filter(
        role='student'
    ).order_by('-date_joined')[:5]

    recent_exams = Exam.objects.order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_exams': total_exams,
        'total_attempts': total_attempts,
        'recent_students': recent_students,
        'recent_exams': recent_exams,
    }
    return render(request, 'users/admin_dashboard.html', context)


# ============================================================
# HELPER FUNCTION
# ============================================================
def redirect_to_dashboard(user):
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')

# ============================================================
# ADMIN — User Management
# ============================================================
@login_required
def manage_users(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied!')
        return redirect('admin_dashboard')

    students = User.objects.filter(role='student').order_by('-date_joined')
    teachers = User.objects.filter(role='teacher').order_by('-date_joined')

    return render(request, 'users/manage_users.html', {
        'students': students,
        'teachers': teachers,
    })


@login_required
def delete_user(request, user_id):
    if not request.user.is_admin():
        messages.error(request, 'Access denied!')
        return redirect('admin_dashboard')

    user = get_object_or_404(User, id=user_id)

    if user.is_superuser:
        messages.error(request, 'Cannot delete superuser!')
        return redirect('manage_users')

    username = user.username
    user.delete()
    messages.success(request, f'User "{username}" deleted successfully!')
    return redirect('manage_users')


@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_admin():
        return redirect('admin_dashboard')

    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status}!')
    return redirect('manage_users')


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.roll_number = request.POST.get('roll_number', '')
        user.course = request.POST.get('course', '')

        # Password change
        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
            messages.success(request, 'Password changed! Please login again.')

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'users/profile.html')
