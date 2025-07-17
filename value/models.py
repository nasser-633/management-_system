from django.db import models
from django.contrib.auth.models import AbstractUser


# 🔷 User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


# 🔷 Core models
class Classroom(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# 🔷 Teacher & Student
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    classes = models.ManyToManyField(Classroom)
    Grade = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


# 🔷 Attendance & Salary
class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)


class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)


class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()


class TeacherSalaryHistory(models.Model):
    teacher_salary = models.ForeignKey(TeacherSalary, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    old_amount = models.DecimalField(max_digits=8, decimal_places=2)
    new_amount = models.DecimalField(max_digits=8, decimal_places=2)


# 🔷 Exams
class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()


class StudentExam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks = models.IntegerField()


class ExamGrade(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)


class ExamTimetable(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    notes = models.TextField()


class StudentGrade(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)


# 🔷 Events
class EventCategory(models.Model):
    name = models.CharField(max_length=50)


class EventCategoryType(models.Model):
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Event(models.Model):
    name = models.CharField(max_length=100)
    category_type = models.ForeignKey(EventCategoryType, on_delete=models.CASCADE)
    date = models.DateField()


# 🔷 Payments
class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()


class StudentPaymentHistory(models.Model):
    payment = models.ForeignKey(StudentPayment, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    old_amount = models.DecimalField(max_digits=8, decimal_places=2)
    new_amount = models.DecimalField(max_digits=8, decimal_places=2)


class PaymentNotifications(models.Model):
    payment = models.ForeignKey(StudentPayment, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)


# 🔷 Chat & Notifications
class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_chats', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_chats', on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


class GroupMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


class MyFriends(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)


class MainNotification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(MainNotification, on_delete=models.CASCADE)
    read_at = models.DateTimeField(null=True, blank=True)


class OnlineChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)


class CriticalHistory(models.Model):
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Temporary(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# 🔷 Subject Routine
class SubjectRoutine(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
class PettyCash(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)      
    
class PettyCashHistory(models.Model):
    pettyCash = models.ForeignKey(PettyCash, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    old_amount = models.DecimalField(max_digits=10, decimal_places=2)
    new_amount = models.DecimalField(max_digits=10, decimal_places=2)   
    
class Grade(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Timetable(models.Model):  
    class_name = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.class_name} - {self.subject} ({self.day_of_week})"
    
    
           
