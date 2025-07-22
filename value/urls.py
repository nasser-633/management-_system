# In your app's urls.py
from django.urls import path
from . import views

app_name = 'value'

urlpatterns = [
    # Root URL points to your home view
    path('', views.home, name='home'), # <--- ADDED THIS LINE

    # Authentication views
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    # Admin Dashboard main entry (from sidebar "Dashboard")
    path('dashboard/', views.dashboard_home, name='dashboard_home'),

    # Role-based Dashboards (Keep if still used for specific roles)
    # path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'), # Now redundant with dashboard_home, consider removing this line
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),

    # Comprehensive Admin Dashboard Sections (These are now the main ones)
    path('dashboard/users/', views.user_list, name='dashboard_user_list'),
    path('dashboard/students/', views.student_list, name='dashboard_student_list'),
    path('dashboard/teachers/', views.teacher_list, name='dashboard_teacher_list'),
    path('dashboard/classrooms/', views.classroom_list, name='dashboard_classroom_list'),

    # MODIFIED: These now load within the admin_dashboard.html
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('petty-cash/', views.petty_cash_list, name='petty_cash_list'),
    path('chat/', views.chat_room, name='chat_room'),
    path('group-chat/', views.group_chat, name='group_chat'),
    path('friends/', views.friends_list, name='friends_list'),

    # Keep these if you still need them for non-admin users or other purposes
    # path('students/', views.student_list, name='student_list'),
    # path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
]