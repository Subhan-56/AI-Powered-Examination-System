from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    role = forms.ChoiceField(choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ])

    class Meta:
        model = User
        fields = [
            'username',
            'first_name', 
            'last_name',
            'email',
            'role',
            'password1',
            'password2'
        ]