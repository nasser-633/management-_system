from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from .forms import UserCreationForm, ClassroomForm, FeeForm, EventForm, PettyCashForm # Ensure these are available

# Import your custom models
from .models import Student, Classroom, Teacher, Subject, Event, StudentPayment, Exam, Chat, GroupMessage, MyFriends, MainNotification, PettyCash, Parent

# Get the custom User model
User = get_user_model()

# --- Helper function to get common dashboard context ---
def get_dashboard_common_context():
    return {
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classrooms': Classroom.objects.count(),
        'notifications': MainNotification.objects.order_by('-created_at')[:5],
        'students_overview': Student.objects.select_related('user', 'student_class').all()[:5],
        'teachers_overview': Teacher.objects.select_related('user').all()[:5],
        'classrooms_overview': Classroom.objects.all(),
        'events_overview': Event.objects.all().order_by('-date')[:5],
        'petty_cash_overview': PettyCash.objects.all().order_by('-date')[:5],
        'chats_overview': Chat.objects.all().order_by('-sent_at')[:5],
        'group_chats_overview': GroupMessage.objects.all().order_by('-sent_at')[:5],
        'classroom_form': ClassroomForm(), # Added for "Add Classroom" functionality
        'add_student_form': UserCreationForm(), # Added for "Add Student" functionality
    }

# --- Existing Views (Keep as is unless specified) ---

# Home page
def home(request):
    return render(request, 'home.html')

# User registration view (keep as is)
def register(request):
    context = {'username_attempt': '', 'selected_role': ''}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        context['username_attempt'] = username
        context['selected_role'] = role

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

        if not role:
            messages.error(request, "Please select a role (Teacher, Parent, or Student).")
            return render(request, 'register.html', context)

        try:
            user = User.objects.create_user(username=username, password=password, role=role)

            if role == 'student':
                Student.objects.create(user=user)
            elif role == 'teacher':
                Teacher.objects.create(user=user)
            elif role == 'parent':
                Parent.objects.create(user=user)

            messages.success(request, f"Registration successful as {role.capitalize()}. Please log in.")
            return redirect('value:login_view')

        except Exception as e:
            messages.error(request, f"An unexpected error occurred during registration: {e}")
            return render(request, 'register.html', context)

    return render(request, 'register.html', context)

# User login view (keep as is)
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

            # Redirect directly to dashboard_home for admin/staff
            if user.is_superuser or user.is_staff:
                return redirect('value:dashboard_home')
            elif user.role == 'teacher':
                return redirect('value:teacher_dashboard')
            elif user.role == 'parent':
                return redirect('value:parent_dashboard')
            elif user.role == 'student':
                return redirect('value:student_dashboard')
            else:
                return redirect('value:home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', context)

    return render(request, 'login.html', context)

# User logout (keep as is)
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('value:home')

# Existing Role-Specific Dashboards (admin_dashboard is now largely redundant with dashboard_home)
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the admin dashboard.")
        return redirect('value:home')

    # This view is now largely superseded by dashboard_home.
    # It's better to just redirect to dashboard_home if admin_dashboard is still mapped in urls.
    return redirect('value:dashboard_home')


@login_required
def teacher_dashboard(request):
    if not request.user.role == 'teacher' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the teacher dashboard.")
        return redirect('value:home')
    return render(request, 'teacher/dashboard.html')

@login_required
def student_dashboard(request):
    if not request.user.role == 'student' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the student dashboard.")
        return redirect('value:home')
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def parent_dashboard(request):
    if not request.user.role == 'parent' and not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access the parent dashboard.")
        return redirect('value:home')
    parent_profile = get_object_or_404(Parent.objects.select_related('user', 'student__user', 'student__student_class'), user=request.user)
    context = {
        'parent_profile': parent_profile,
    }
    return render(request, 'parent/dashboard.html', context)

# --- NEW Comprehensive Admin Dashboard Views (MODIFIED) ---

@login_required
def dashboard_home(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this dashboard.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['active_view'] = 'home' # Default to showing the home/overview section

    # The add/delete student forms will now post to specific views,
    # so we don't need action handling here.
    return render(request, 'admin/admin_dashboard.html', context)

# --- Student Management Actions (New/Modified) ---

@login_required
def add_student(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to add students.")
        return redirect('value:dashboard_home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.role = 'student' # Set the role explicitly
                user.save()
                Student.objects.create(user=user)
                messages.success(request, f"Student {user.username} added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding student: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect('value:dashboard_home') # Redirect back to the dashboard home or student list


@login_required
def delete_student(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to delete students.")
        return redirect('value:dashboard_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            user = User.objects.filter(username=username, role='student').first()
            if user:
                user.delete()
                messages.success(request, f"Student {username} deleted.")
            else:
                messages.error(request, "Student not found.")
        else:
            messages.error(request, "Username for deletion cannot be empty.")
    return redirect('value:dashboard_home')


@login_required
def user_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['users'] = User.objects.all().order_by('username')
    context['active_view'] = 'users'
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def student_list(request):
    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'parent' or request.user.role == 'teacher'):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['students'] = Student.objects.select_related('user', 'student_class').order_by('user__username')
    context['active_view'] = 'students'
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def classroom_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['classrooms'] = Classroom.objects.all().order_by('name')
    context['active_view'] = 'classrooms'
    context['form'] = ClassroomForm() # For the "Add Classroom" form in the template
    return render(request, 'admin/admin_dashboard.html', context)

# --- NEW: Classroom Management Views ---
@login_required
def add_classroom(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to add classrooms.")
        return redirect('value:dashboard_home') # Redirect to a safe place

    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Classroom added successfully.")
            return redirect('value:dashboard_classroom_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # If form is invalid, you might want to re-render the classroom_list with the form errors
            # For simplicity, we'll redirect back to the list and messages will show errors
            return redirect('value:dashboard_classroom_list')
    # If not POST request, just redirect to the list view (shouldn't be accessed directly)
    return redirect('value:dashboard_classroom_list')


@login_required
def edit_classroom(request, pk):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to edit classrooms.")
        return redirect('value:dashboard_home')

    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, f"Classroom '{classroom.name}' updated successfully.")
            return redirect('value:dashboard_classroom_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # If form is invalid, re-render the edit form with errors
            context = get_dashboard_common_context()
            context['active_view'] = 'edit_classroom'
            context['form'] = form
            context['editing_classroom'] = classroom
            return render(request, 'admin/admin_dashboard.html', context)
    else:
        form = ClassroomForm(instance=classroom)

    context = get_dashboard_common_context()
    context['active_view'] = 'edit_classroom' # Set active view for the template
    context['form'] = form
    context['editing_classroom'] = classroom # Pass the object being edited
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def delete_classroom(request, pk):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to delete classrooms.")
        return redirect('value:dashboard_home')

    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        try:
            classroom.delete()
            messages.success(request, f"Classroom '{classroom.name}' deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting classroom: {e}")
    else:
        messages.error(request, "Invalid request method for deleting classroom.")
    return redirect('value:dashboard_classroom_list')

# --- Classroom Detail View (If you want a dedicated detail page within dashboard) ---
@login_required
def classroom_detail(request, pk):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to view classroom details.")
        return redirect('value:dashboard_home')

    classroom = get_object_or_404(Classroom, pk=pk)
    context = get_dashboard_common_context()
    context['active_view'] = 'classroom_detail'
    context['classroom_detail'] = classroom # Data for the detail view
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def teacher_list(request):
    if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'admin'):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['teachers'] = Teacher.objects.select_related('user').prefetch_related('subjects', 'classes').order_by('user__username')
    context['active_view'] = 'teachers'
    return render(request, 'admin/admin_dashboard.html', context)

# --- MODIFIED: Events, Payments, Exams, Chats, Group Chats, Friends List ---
# These now render inside the admin/admin_dashboard.html

@login_required
def event_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['events'] = Event.objects.all().order_by('-date')
    context['active_view'] = 'events'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    context = get_dashboard_common_context()
    context['event_detail'] = event
    context['active_view'] = 'event_detail'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def payment_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['payments'] = StudentPayment.objects.all().order_by('-date')
    context['active_view'] = 'payments'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(StudentPayment, pk=payment_id)
    context = get_dashboard_common_context()
    context['payment_detail'] = payment
    context['active_view'] = 'payment_detail'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def exam_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['exams'] = Exam.objects.all().order_by('-date')
    context['active_view'] = 'exams'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    context = get_dashboard_common_context()
    context['exam_detail'] = exam
    context['active_view'] = 'exam_detail'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def petty_cash_list(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['petty_cash_entries'] = PettyCash.objects.all().order_by('-date')
    context['active_view'] = 'petty_cash'
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def chat_room(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.role in ['teacher', 'student', 'parent']:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    # For a general chat_room, you might want messages involving the current user, or all if admin
    if request.user.is_superuser or request.user.is_staff:
        context['chat_messages'] = Chat.objects.all().order_by('sent_at')[:50]
    else:
        # Fetch messages where current user is sender or receiver
        context['chat_messages'] = Chat.objects.filter(sender=request.user).order_by('sent_at')[:50] # Simplified, you'd typically filter by conversation
        # Or, get messages from specific conversations accessible to the user

    context['users_for_chat'] = User.objects.exclude(pk=request.user.pk).all() # Users for selecting a recipient
    context['active_view'] = 'chat_room'

    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id')
        if message_text and receiver_id:
            try:
                receiver_user = User.objects.get(pk=receiver_id)
                Chat.objects.create(sender=request.user, receiver=receiver_user, message=message_text)
                messages.success(request, "Your message has been sent!")
            except User.DoesNotExist:
                messages.error(request, "Receiver user not found.")
        else:
            messages.error(request, "Message or receiver cannot be empty.")
        return redirect('value:chat_room')

    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def group_chat(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.role in ['teacher', 'student', 'parent']:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    context['group_messages'] = GroupMessage.objects.all().order_by('sent_at')[:50]
    context['active_view'] = 'group_chat'

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            GroupMessage.objects.create(sender=request.user, message=message_text)
            messages.success(request, "Your group message has been sent!")
        else:
            messages.error(request, "Message cannot be empty.")
        return redirect('value:group_chat')

    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def friends_list(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.role in ['teacher', 'student', 'parent']:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('value:home')

    context = get_dashboard_common_context()
    # For an admin, you might want to see all friend relationships,
    # or just the ones involving the current user if the 'friends_list' is universal.
    # Assuming 'MyFriends' is a relationship, filter for the logged-in user's friends.
    # If this is for admin to manage all friendships, adjust the filter.
    context['friends'] = MyFriends.objects.filter(user=request.user).select_related('friend')
    context['active_view'] = 'friends_list'
    return render(request, 'admin/admin_dashboard.html', context)


# Keep student_detail and teacher_detail and integrate them into the admin_dashboard
@login_required
def student_detail(request, student_id):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.role in ['parent', 'teacher']:
        messages.warning(request, "You do not have permission to view student details.")
        return redirect('value:home')

    student = get_object_or_404(Student.objects.select_related('user', 'student_class'), pk=student_id)
    context = get_dashboard_common_context()
    context['student_detail'] = student
    context['active_view'] = 'student_detail' # New active_view state for student detail
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def teacher_detail(request, teacher_id):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.role in ['admin']:
        messages.warning(request, "You do not have permission to view teacher details.")
        return redirect('value:home')

    teacher = get_object_or_404(Teacher.objects.select_related('user'), pk=teacher_id)
    context = get_dashboard_common_context()
    context['teacher_detail'] = teacher
    context['active_view'] = 'teacher_detail' # New active_view state for teacher detail
    return render(request, 'admin/admin_dashboard.html', context)