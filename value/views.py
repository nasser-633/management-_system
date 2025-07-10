from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group # <--- IMPORT GROUP HERE
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Home page
def home(request):
    return render(request, 'home.html')

User = get_user_model() 

# User registration view
def register(request):
    context = {'username_attempt': '', 'selected_role': ''} # Initialize selected_role

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role') # <--- GET THE SELECTED ROLE

        context['username_attempt'] = username 
        context['selected_role'] = role # Pass selected role back for re-selection on error

        # Input Validation (add role validation)
        if not username:
            messages.error(request, "Username cannot be empty.")
            return render(request, 'register.html', context)

        if not password:
            messages.error(request, "Password cannot be empty.")
            return render(request, 'register.html', context)

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html', context)

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists. Please choose a different one.")
            return render(request, 'register.html', context)
            
        # NEW: Validate if a role was selected
        if not role:
            messages.error(request, "Please select a role (Teacher, Parent, or Student).")
            return render(request, 'register.html', context)

        try:
            user = User.objects.create_user(username=username, password=password)
            
            # NEW: Assign user to the selected group/role
            try:
                # Group names should be lowercase to match values in HTML
                user_group = Group.objects.get(name=role.capitalize()) # Assuming groups are "Teacher", "Parent", "Student"
                user.groups.add(user_group)
                messages.success(request, f"Registration successful as {role.capitalize()}. Please log in.")
                return redirect('login_view') 
            except Group.DoesNotExist:
                messages.error(request, f"Error: Role '{role.capitalize()}' does not exist. Please contact support.")
                user.delete() # Clean up the user if group assignment failed
                return render(request, 'register.html', context)

        except Exception as e:
            messages.error(request, f"An unexpected error occurred during registration: {e}")
            return render(request, 'register.html', context)

    return render(request, 'register.html', context)


# User login view
def login_view(request):
    context = {'username_attempt': ''}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        context['username_attempt'] = username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # NEW: Redirect based on user's role/group
            if user.is_superuser or user.is_staff: 
                return redirect('admin_dashboard')
            elif user.groups.filter(name='Teacher').exists():
                return redirect('teacher_dashboard')
            elif user.groups.filter(name='Parent').exists():
                return redirect('parent_dashboard')
            elif user.groups.filter(name='Student').exists():
                return redirect('student_dashboard')
            else: # Fallback for users with no specific role or other roles
                return redirect('home') 
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', context)

    return render(request, 'login.html', context)


# User logout
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the admin dashboard.")
        return redirect('home')
    return render(request, 'admin_dashboard.html')


# Teacher Dashboard
@login_required
def teacher_dashboard(request):
    # Ensure only teachers can access this
    if not request.user.groups.filter(name='Teacher').exists() and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the teacher dashboard.")
        return redirect('home')
    return render(request, 'teacher_dashboard.html')

# Student Dashboard
@login_required
def student_dashboard(request):
    # Ensure only students can access this
    if not request.user.groups.filter(name='Student').exists() and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the student dashboard.")
        return redirect('home')
    student = request.user  # or fetch a specific Student profile linked to request.user
    context = {
        'student': student,
        # Add other student-specific data here
    }
    return render(request, 'student_dashboard.html', context)

# Parent Dashboard
@login_required
def parent_dashboard(request):
    # Add logic to ensure only parents can access this dashboard
    if not request.user.groups.filter(name='Parent').exists() and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the parent dashboard.")
        return redirect('home')
    return render(request, 'parent_dashboard.html')


# (Rest of your views.py functions remain the same)
# List of students
@login_required
def student_list(request):
    # Assuming students are users who are not staff/superusers. Adjust if you have a separate Student model.
    students = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    return render(request, 'student_list.html', {'students': students})

# Student detail
@login_required
def student_detail(request, student_id):
    student = get_object_or_404(User, pk=student_id)
    return render(request, 'student_detail.html', {'student': student})

# Teacher list
@login_required    
def teacher_list(request):
    # Assuming teachers are users who are staff but not superusers. Adjust if you have a separate Teacher model.
    teachers = User.objects.filter(is_staff=True, is_superuser=False).order_by('username')  
    return render(request, 'teacher_list.html', {'teachers': teachers}) 

# Teacher detail
@login_required    
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(User, pk=teacher_id)
    return render(request, 'teacher_detail.html', {'teacher': teacher}) 

# Event list
@login_required 
def event_list(request):
    events = [] # Placeholder if Event model not yet implemented
    messages.info(request, "Event list functionality is under development.") # Example message
    return render(request, 'event_list.html', {'events': events})    

# Event detail    
@login_required 
def event_detail(request, event_id):
    messages.error(request, "Event model not implemented or event not found.")
    return redirect('event_list')

# Payment list
@login_required 
def payment_list(request):
    payments = [] # Placeholder if StudentPayment model not yet implemented
    messages.info(request, "Payment list functionality is under development.")
    return render(request, 'payment_list.html', {'payments': payments}) 

# Payment detail
@login_required 
def payment_detail(request, payment_id):
    messages.error(request, "Payment model not implemented or payment not found.")
    return redirect('payment_list')

# Exam list
@login_required
def exam_list(request):
    exams = [] # Placeholder if Exam model not yet implemented
    messages.info(request, "Exam list functionality is under development.")
    return render(request, 'exam_list.html', {'exams': exams})

# Exam detail
@login_required
def exam_detail(request, exam_id):
    messages.error(request, "Exam model not implemented or exam not found.")
    return redirect('exam_list')

# Chat room
@login_required
def chat_room(request):
    chat_messages = [] # Placeholder if ChatMessage model not yet implemented
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            messages.success(request, "Your message has been sent!")
            return redirect('chat_room') 
        else:
            messages.error(request, "Message cannot be empty.")
    return render(request, 'chat_room.html', {'messages': chat_messages})

# Group chat
@login_required
def group_chat(request):
    group_messages = [] # Placeholder if GroupMessage model not yet implemented
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            messages.success(request, "Your group message has been sent!")
            return redirect('group_chat') 
        else:
            messages.error(request, "Message cannot be empty.")
    return render(request, 'group_chat.html', {'messages': group_messages})

# Friends list
@login_required
def friends_list(request):
    friends = [] # Placeholder if Friendship model not yet implemented
    messages.info(request, "Friends list functionality is under development.")
    return render(request, 'friends_list.html', {'friends': friends})