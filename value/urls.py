# value/urls.py
from django.urls import path
from . import views

app_name = 'value' # Added namespace for your app's URLs

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    # Existing dashboard paths (keeping them for now)
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),

    # New Admin Dashboard paths (these will be the comprehensive dashboard)
    # The main entry point for the new admin dashboard
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/users/', views.user_list, name='dashboard_user_list'), # Renamed name to avoid conflict
    path('dashboard/students/', views.student_list, name='dashboard_student_list'), # Renamed name to avoid conflict
    path('dashboard/classrooms/', views.classroom_list, name='dashboard_classroom_list'), # Renamed name to avoid conflict

    # Existing list/detail views (keeping them, they might be used elsewhere)
    path('students/', views.student_list, name='student_list'), # Existing student list
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),

    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),

    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    path('payments/', views.payment_list, name='payment_list'),
    path('payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),

    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),

    path('chat/', views.chat_room, name='chat_room'),
    path('group_chat/', views.group_chat, name='group_chat'),
    path('friends/', views.friends_list, name='friends_list'),
]
