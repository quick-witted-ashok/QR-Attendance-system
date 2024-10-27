from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CustomUser
import qrcode
from django.conf import settings
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import QRCode, Classroom


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'faculty':
                return redirect('faculty_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
        else:
            return render(request, 'attendance/login.html', {'error': 'Invalid credentials'})
    return render(request, 'attendance/login.html')


from django.contrib.auth.decorators import login_required
from .models import Classroom, AttendanceRecord

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')
    # Fetch the student's attendance records
    attendance_records = AttendanceRecord.objects.filter(student=request.user)
    return render(request, 'attendance/student_dashboard.html', {'attendance_records': attendance_records})

from django.shortcuts import render
from .models import Classroom

@login_required
def faculty_dashboard(request):
    if request.user.role != 'faculty':
        return redirect('login')

    # Get the classes managed by the faculty
    classrooms = Classroom.objects.filter(faculty=request.user)

    return render(request, 'attendance/faculty_dashboard.html', {
        'classrooms': classrooms,
    })

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')
    # Overview of all users, classrooms, and attendance records
    students = CustomUser.objects.filter(role='student')
    faculty = CustomUser.objects.filter(role='faculty')
    classrooms = Classroom.objects.all()
    return render(request, 'attendance/admin_dashboard.html', {
        'students': students,
        'faculty': faculty,
        'classrooms': classrooms
    })



import datetime
import qrcode
import os
import socket
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from pytz import timezone

def generate_qr_code(request, classroom_id):
    # Get the local IP address of the server
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # Set expiration time (4 minutes from now) in UTC
    expiration_time = timezone.now() + timedelta(minutes=4)

    # Generate the QR code URL with expiration time
    qr_code_url = f"http://{local_ip}:8000/attendance/{classroom_id}/scan/?expiry_time={expiration_time.isoformat()}"
    
    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_url)
    qr.make(fit=True)

    print(qr_code_url)

    # Save the QR code image
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_code_dir, exist_ok=True)
    qr_code_path = os.path.join(qr_code_dir, f'{classroom_id}_qr.png')
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(qr_code_path)

    return render(request, 'attendance/generate_qr_code.html', {
        'qr_code_path': f"{settings.MEDIA_URL}qrcodes/{classroom_id}_qr.png",
        'expiration_time': expiration_time.isoformat(),
        'classroom_id': classroom_id
    })




from .models import Classroom, Student
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse

def scan_qr_code(request, classroom_id):
    expiry_time_str = request.GET.get('expiry_time')

    print("Query Parameters:", request.GET)
    print("Received Expiry Time String:", expiry_time_str)

    if not expiry_time_str:
        return JsonResponse({'error': 'Expiry time missing.'}, status=400)

    # Parse the expiry time
    expiry_time = parse_datetime(expiry_time_str)

    print("Parsed Expiry Time:", expiry_time)

    # Check if expiry_time is None (parsing failed)
    if expiry_time is None:
        return JsonResponse({'error': 'Invalid expiry time format.'}, status=400)

    # If the expiry time is naive, make it aware by assuming it's in UTC
    if timezone.is_naive(expiry_time):
        expiry_time = timezone.make_aware(expiry_time, timezone=timezone.utc)

    # Check if the expiry time is in the past
    if expiry_time < timezone.now():
        return JsonResponse({'error': 'QR code has expired or is invalid.'}, status=400)

    # Continue with retrieving classroom and students
    try:
        classroom = Classroom.objects.get(id=classroom_id)
        students = Student.objects.filter(classroom=classroom).values('id', 'name')
        student_list = list(students)

        print("Student List:", student_list)
    except Classroom.DoesNotExist:
        return JsonResponse({'error': 'Classroom not found.'}, status=404)

    return JsonResponse({'students': student_list}, status=200)

# Mark Attendance for Selected Student
def mark_attendance(request, classroom_id):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        student = get_object_or_404(Student, id=student_id)

        # Record attendance
        AttendanceRecord.objects.create(
            student=student,
            classroom=classroom,
            status="Present",
            date=timezone.now().date()
        )
        return redirect('attendance_success')  # Redirect to success or confirmation page

    return redirect('scan_qr_code', classroom_id=classroom_id)

# Display Classroom Students
@login_required
def classroom_students(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = classroom.students.all()  # Adjust model relationship if necessary
    return render(request, 'attendance/classroom_students.html', {'classroom': classroom, 'students': students})

# def scan_qr_code(request, classroom_id):
#     if request.method == "GET":
#         # Get the expiry time from the request query parameter
#         expiry_time_str = request.GET.get('expiry_time')

#         if expiry_time_str:
#             # Remove any leading/trailing spaces
#             expiry_time_str = expiry_time_str.strip()
#             print("Received expiry time:", expiry_time_str)

#             # Attempt to parse the expiry time
#             expiry_time = parse_datetime(expiry_time_str)

#             # If parsing failed, respond with an error
#             if expiry_time is None:
#                 return JsonResponse({'error': 'Invalid expiry time format. Please ensure it is in ISO 8601 format.'}, status=400)

#             # Ensure expiry_time is timezone-aware
#             if timezone.is_naive(expiry_time):
#                 expiry_time = timezone.make_aware(expiry_time)

#             # Compare with current time to check if expired
#             if timezone.now() > expiry_time:
#                 return JsonResponse({'error': 'QR code has expired.'}, status=400)

#         # Retrieve students for the classroom
#         try:
#             classroom = Classroom.objects.get(id=classroom_id)
#             students = classroom.students.all()
#             student_ids = [{'id': student.user.id, 'name': student.name} for student in students]
#         except Classroom.DoesNotExist:
#             return JsonResponse({'error': 'Classroom not found.'}, status=404)
        
#         print("Received expiry time:", expiry_time_str)


#         # Return student IDs to the front-end or mobile client
#         return JsonResponse({
#             'message': 'Scan successful',
#             'students': student_ids,
#             'classroom_id': classroom_id
#         })

#     return JsonResponse({'error': 'Invalid request.'}, status=400)


from django.shortcuts import render
from .models import AttendanceRecord  # Import your attendance model

def view_attendance(request, classroom_id):
    # Fetch attendance records for the specified classroom
    attendance_records = AttendanceRecord.objects.filter(classroom_id=classroom_id)
    return render(request, 'attendance/view_attendance.html', {
        'attendance_records': attendance_records,
        'classroom_id': classroom_id,
    })



# def mark_attendance(request, classroom_id):
#     if request.method == "POST":
#         student_id = request.POST.get('student_id')
#         date = request.POST.get('date', timezone.now().date())  # Use today's date if none provided
        
#         # Save attendance record
#         attendance_record = Student.objects.create(
#             student_id=student_id,
#             classroom_id=classroom_id,
#             date=date
#         )
        
#         return redirect('faculty_dashboard')  # Redirect to dashboard or wherever needed




def select_student(request, classroom_id):
    if request.method == 'GET':
        students = Student.objects.filter(classroom_id=classroom_id)
        return render(request, 'attendance/select_student.html', {'students': students, 'classroom_id': classroom_id})



from django.shortcuts import render, get_object_or_404
from .models import Classroom, Student  # Adjust based on your models

def attendance_page(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = Student.objects.filter(classroom=classroom)  # Adjust based on your relationship

    if request.method == 'POST':
        # Handle attendance submission logic here
        selected_students = request.POST.getlist('selected_students')
        # Logic to save attendance to the database
        
    return render(request, 'attendance/attendance_page.html', {
        'classroom': classroom,
        'students': students,
    })


# attendance/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Classroom, Student
from .forms import AddStudentForm

@login_required
def add_student(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == "POST":
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.classroom = classroom
            student.save()
            return redirect('classroom_detail', classroom_id=classroom.id)
    else:
        form = AddStudentForm(initial={'classroom': classroom})
    return render(request, 'attendance/add_student.html', {'form': form, 'classroom': classroom})



def classroom_detail(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    return render(request, 'attendance/classroom_detail.html', {'classroom': classroom})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Classroom, Student
from .forms import AddStudentToClassroomForm

def add_student_to_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if request.method == 'POST':
        form = AddStudentToClassroomForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            try:
                classroom.students.add(student)  # Add the student to the classroom
                messages.success(request, f"{student.name} has been added to {classroom.name}.")
                return redirect('classroom_detail', classroom_id=classroom.id)
            except Exception as e:
                messages.error(request, f"An error occurred while adding the student: {str(e)}")
        else:
            messages.error(request, "Please select a valid student.")
    else:
        form = AddStudentToClassroomForm()

    return render(request, 'attendance/add_student_to_classroom.html', {'form': form, 'classroom': classroom})


# viey

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Classroom, Student  # Adjust model names if necessary

# For rendering HTML instead of JSON

def get_students_in_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = classroom.students.all()
    
    return render(request, 'students_list.html', {
        'students': students,
        'classroom_id': classroom.id,
    })
