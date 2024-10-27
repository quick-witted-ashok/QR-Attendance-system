from django.urls import path
from . import views
from .views import faculty_dashboard,classroom_students,mark_attendance, generate_qr_code, view_attendance,attendance_page,scan_qr_code,student_dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

# urlpatterns = [
#     path('login/', views.user_login, name='login'),
#     path('dashboard/student/', student_dashboard, name='student_dashboard'),
#     path('dashboard/faculty/', faculty_dashboard, name='faculty_dashboard'),
#     path('generate_qr_code/<int:classroom_id>/', generate_qr_code, name='generate_qr_code'),
#     path('attendance/<int:classroom_id>/', scan_qr_code, name='scan_qr_code'),  # Add this for scanning
#     # path('classroom/<int:classroom_id>/add_student/', views.add_student, name='add_student'),
#     path('classroom/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
#     path('scan_qr_code/', scan_qr_code, name='scan_qr_code'),
#     path('select_student/<int:classroom_id>/', views.select_student, name='select_student'),
#     path('mark_attendance/<int:classroom_id>/', views.mark_attendance, name='mark_attendance'),
#     path('attendance/<int:classroom_id>/', attendance_page, name='attendance_page'),
#     path('view_attendance/<int:classroom_id>/', views.view_attendance, name='view_attendance'), 
#     path('classroom/<int:classroom_id>/students/', classroom_students, name='classroom_students'),

#     path('classroom/<int:classroom_id>/add_student/', views.add_student_to_classroom, name='add_student_to_classroom'), # Add this line
# ] 

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/faculty/', faculty_dashboard, name='faculty_dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('generate_qr_code/', generate_qr_code, name='generate_qr_code'),
    # path('attendance/<int:classroom_id>/', scan_qr_code, name='scan_qr_code'),

    path('generate_qr_code/<int:classroom_id>/', views.generate_qr_code, name='generate_qr_code'),
    path('attendance/<int:classroom_id>/scan/', views.scan_qr_code, name='scan_qr_code'),
    path('attendance/<int:classroom_id>/mark/', views.mark_attendance, name='mark_attendance'),

    path('classroom/<int:classroom_id>/students/', views.classroom_students, name='classroom_students'),



    path('classroom/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
    path('select_student/<int:classroom_id>/', views.select_student, name='select_student'),

    path('mark_attendance/<int:classroom_id>/', mark_attendance, name='mark_attendance'),


    # path('mark_attendance/<int:classroom_id>/', views.mark_attendance, name='mark_attendance'),
    path('view_attendance/<int:classroom_id>/', views.view_attendance, name='view_attendance'), 
   
    
     path('classroom/<int:classroom_id>/students/', views.get_students_in_classroom, name='get_students_in_classroom'),


    path('classroom/<int:classroom_id>/add_student/', views.add_student_to_classroom, name='add_student_to_classroom'),
] 


# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Serve media files during development


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)