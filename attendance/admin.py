from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Classroom, AttendanceRecord, QRCode,Student

# admin.site.register(CustomUser)
admin.site.register(Classroom)
admin.site.register(AttendanceRecord)
admin.site.register(QRCode)
admin.site.register(Student)


admin.site.register(CustomUser, UserAdmin)
