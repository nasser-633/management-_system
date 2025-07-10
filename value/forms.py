from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Student, Teacher, Event, Exam

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    pass

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'student_class']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'subjects', 'classes']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'
