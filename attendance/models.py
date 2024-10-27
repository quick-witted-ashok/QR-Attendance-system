from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    unique_id = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    students = models.ManyToManyField('Student', related_name='classrooms', blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, default="Absent")

    def __str__(self):
        return f"{self.student.username} - {self.classroom.name} - {self.date}"

class QRCode(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()

    def is_valid(self):
        from django.utils import timezone
        return self.expiry_time > timezone.now()

    def __str__(self):
        return f"QR Code for {self.classroom.name} (Expires: {self.expiry_time})"
