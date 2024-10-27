from django import forms
from .models import Student

class AddStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'name', 'student_id']



class AddStudentToClassroomForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select a student")
