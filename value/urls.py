from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    path('students/', views.student_list, name='student_list'),
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

    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),
]
