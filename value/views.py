from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count # For dashboard home counts


# Import your custom models
# IMPORTANT: Added 'Parent' to this import list
from .models import Student, Classroom, Teacher, Subject, Event, StudentPayment, Exam, Chat, GroupMessage, MyFriends, MainNotification, PettyCash, Parent

# Get the custom User model
User = get_user_model()

# --- Existing Views ---

# Home page
def home(request):
    return render(request, 'home.html')

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
            user = User.objects.create_user(username=username, password=password, role=role) # Assign role directly if User model has a 'role' field

            # If you're still using Django's Group model for roles:
            # from django.contrib.auth.models import Group
            # try:
            #     user_group = Group.objects.get(name=role.capitalize()) # Assuming groups are "Teacher", "Parent", "Student"
            #     user.groups.add(user_group)
            # except Group.DoesNotExist:
            #     messages.error(request, f"Error: Role '{role.capitalize()}' group does not exist. Please contact support.")
            #     user.delete() # Clean up the user if group assignment failed
            #     return render(request, 'register.html', context)

            # Create associated profile (Student, Teacher, Parent)
            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'teacher':
                Teacher.objects.create(user=user)
            elif role == 'parent':
                Parent.objects.create(user=user)

            messages.success(request, f"Registration successful as {role.capitalize()}. Please log in.")
            return redirect('value:login_view') # Use namespaced URL

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

            # Redirect based on user's role/group
            if user.is_superuser or user.is_staff:
                return redirect('value:dashboard_home') # Redirect to the new comprehensive admin dashboard
            elif user.role == 'teacher': # Assuming 'role' field on User model
                return redirect('value:teacher_dashboard')
            elif user.role == 'parent':
                return redirect('value:parent_dashboard')
            elif user.role == 'student':
                return redirect('value:student_dashboard')
            else: # Fallback for users with no specific role or other roles
                return redirect('value:home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', context)

    return render(request, 'login.html', context)


# User logout
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('value:home') # Use namespaced URL


# Existing Role-Specific Dashboards (kept as-is for now)
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the admin dashboard.")
        return redirect('value:home')
    return render(request, 'admin_dashboard.html')

@login_required
def teacher_dashboard(request):
    if not request.user.role == 'teacher' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the teacher dashboard.")
        return redirect('value:home')
    return render(request, 'teacher/dashboard.html') # Corrected path here

@login_required
def student_dashboard(request):
    if not request.user.role == 'student' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the student dashboard.")
        return redirect('value:home')
    student = Student.objects.get(user=request.user) # Fetch the Student profile
    context = {
        'student': student,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def parent_dashboard(request):
    if not request.user.role == 'parent' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the parent dashboard.")
        return redirect('value:home')
    # IMPORTANT: Corrected template path here
    # Fetch the Parent profile linked to the current user
    # Use select_related to get the associated Student and its User/Classroom efficiently
    parent_profile = get_object_or_404(Parent.objects.select_related('user', 'student__user', 'student__student_class'), user=request.user)
    
    context = {
        'parent_profile': parent_profile, # Pass the parent profile to the template
    }
    return render(request, 'parent/dashboard.html', context)


# --- NEW Comprehensive Admin Dashboard Views ---

@login_required
def dashboard_home(request):
    # Ensure only superusers or staff can access this comprehensive dashboard
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this dashboard.")
        return redirect('value:home') # Redirect to a safe page

    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_classrooms = Classroom.objects.count()
    total_teachers = Teacher.objects.count()

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_classrooms': total_classrooms,
        'total_teachers': total_teachers,
        'active_page': 'dashboard_home', # For highlighting active link in sidebar
    }
    return render(request, 'value/dashboard_home.html', context)

@login_required
def user_list(request):
    # Ensure only superusers or staff can access this
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    users = User.objects.all().order_by('username')
    context = {
        'users': users,
        'active_page': 'dashboard_user_list', # Matches URL name from value/urls.py
    }
    return render(request, 'value/users.html', context)

@login_required
def student_list(request):
    # This view is used by both /students/ and /dashboard/students/
    # Ensure only authorized users can access this
    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'parent' or request.user.role == 'teacher'):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    # Fetch students and related user/classroom data efficiently
    students = Student.objects.select_related('user', 'student_class').order_by('user__username')
    context = {
        'students': students,
        'active_page': 'dashboard_student_list', # Matches URL name from value/urls.py
    }
    return render(request, 'value/students.html', context)

@login_required
def classroom_list(request):
    # Ensure only superusers or staff can access this
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    classrooms = Classroom.objects.all().order_by('name')
    context = {
        'classrooms': classrooms,
        'active_page': 'dashboard_classroom_list', # Matches URL name from value/urls.py
    }
    return render(request, 'value/classrooms.html', context)

@login_required
def teacher_list(request):
    # This view is used by both /teachers/ and /dashboard/teachers/
    # Ensure only authorized users can access this
    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'admin'): # Assuming admin can see all teachers
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    teachers = Teacher.objects.select_related('user').prefetch_related('subjects', 'classes').order_by('user__username')
    context = {
        'teachers': teachers,
        'active_page': 'teacher_list', # Keep this name for now, or change to 'dashboard_teacher_list' if you add a specific URL for it.
                                       # For the sidebar link to work, it needs to match the 'name' in urls.py.
    }
    return render(request, 'value/admin/teachers.html', context) # IMPORTANT: Changed template path here

# --- Existing Detail Views (kept as-is, ensure they use your models) ---

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('user', 'student_class'), pk=student_id)
    return render(request, 'student_detail.html', {'student': student})

@login_required
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher.objects.select_related('user'), pk=teacher_id)
    return render(request, 'teacher_detail.html', {'teacher': teacher})

# --- Existing List/Detail Views (placeholders, ensure imports match your models) ---
# Make sure these models (Event, StudentPayment, Exam, Chat, GroupMessage, MyFriends, MainNotification, PettyCash)
# are imported at the top if you plan to use them here.

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date') # Assuming Event model exists
    return render(request, 'event_list.html', {'events': events, 'active_page': 'event_list'})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_detail.html', {'event': event})

@login_required
def payment_list(request):
    payments = StudentPayment.objects.all().order_by('-date') # Assuming StudentPayment model exists
    return render(request, 'payment_list.html', {'payments': payments, 'active_page': 'payment_list'})

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(StudentPayment, pk=payment_id)
    return render(request, 'payment_detail.html', {'payment': payment})

@login_required
def exam_list(request):
    exams = Exam.objects.all().order_by('-date') # Assuming Exam model exists
    return render(request, 'exam_list.html', {'exams': exams, 'active_page': 'exam_list'})

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, 'exam_detail.html', {'exam': exam})

@login_required
def chat_room(request):
    # Assuming Chat model exists for direct messages
    # This might need more complex logic for actual chat rooms
    chat_messages = Chat.objects.filter(sender=request.user).order_by('sent_at')[:50] # Example: last 50 sent by user
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id') # You'd need to get receiver
        if message_text and receiver_id:
            try:
                receiver_user = User.objects.get(pk=receiver_id)
                Chat.objects.create(sender=request.user, receiver=receiver_user, message=message_text)
                messages.success(request, "Your message has been sent!")
                return redirect('value:chat_room')
            except User.DoesNotExist:
                messages.error(request, "Receiver user not found.")
        else:
            messages.error(request, "Message or receiver cannot be empty.")
    return render(request, 'chat_room.html', {'messages': chat_messages, 'active_page': 'chat_room'})

@login_required
def group_chat(request):
    # Assuming GroupMessage model exists
    group_messages = GroupMessage.objects.all().order_by('sent_at')[:50] # Example: last 50 group messages
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            GroupMessage.objects.create(sender=request.user, message=message_text)
            messages.success(request, "Your group message has been sent!")
            return redirect('value:group_chat')
        else:
            messages.error(request, "Message cannot be empty.")
    return render(request, 'group_chat.html', {'messages': group_messages, 'active_page': 'group_chat'})

@login_required
def friends_list(request):
    # Assuming MyFriends model exists
    friends = MyFriends.objects.filter(user=request.user).select_related('friend') # Get friends of current user
    return render(request, 'friends_list.html', {'friends': friends, 'active_page': 'friends_list'})
