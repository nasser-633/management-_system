# value/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Classroom, Teacher, Event, StudentPayment, PettyCash

User = get_user_model()

class UserCreationForm(forms.ModelForm): # Changed to forms.ModelForm
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        required=True
    )
    # Removed 'role' and 'grade' fields from the form directly.
    # 'role' will be set in the view, 'grade' (classroom) will be handled when creating Student profile.

    class Meta:
        model = User
        fields = ['username'] # Only username is directly from the User model for this form
        widgets = {
            'username': forms.TextInput(attrs={'class': 'border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Create the User object
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ClassroomForm(forms.ModelForm): # Changed to forms.ModelForm
    class Meta:
        model = Classroom
        fields = ['name', 'capacity'] # Added 'capacity' field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'capacity': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # For editing, exclude the current instance from the uniqueness check
        if self.instance and Classroom.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This classroom name already exists.")
        elif not self.instance and Classroom.objects.filter(name=name).exists():
            raise forms.ValidationError("This classroom name already exists.")
        return name

    # save method is automatically provided by forms.ModelForm

class FeeForm(forms.Form):
    student = forms.CharField(max_length=150, required=True, help_text="Student username")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    def clean_student(self):
        student_username = self.cleaned_data['student']
        if not User.objects.filter(username=student_username, role='student').exists():
            raise forms.ValidationError("Student not found.")
        return student_username

    def save(self):
        student_user = User.objects.get(username=self.cleaned_data['student'], role='student')
        student_profile = Student.objects.get(user=student_user) # Get the Student profile
        return StudentPayment.objects.create(student=student_profile, amount=self.cleaned_data['amount'])

class EventForm(forms.Form):
    date = forms.DateField(required=True, help_text="Format: YYYY-MM-DD")
    title = forms.CharField(max_length=200, required=True)

    def save(self):
        return Event.objects.create(date=self.cleaned_data['date'], title=self.cleaned_data['title'])

class PettyCashForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    description = forms.CharField(max_length=200, required=True)

    def save(self):
        # Assuming PettyCash model has a 'recorded_by' field linked to User
        # You might need to pass request.user to the form's save method or in the view
        # For now, it creates without 'recorded_by'
        return PettyCash.objects.create(amount=self.cleaned_data['amount'], description=self.cleaned_data['description'])