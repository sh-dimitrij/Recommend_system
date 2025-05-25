# serializers.py
from rest_framework import serializers
from .models import CustomUser, Department, Faculty, Semester

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'short_name']

class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'short_name', 'faculty']

class SemesterSerializer(serializers.ModelSerializer):
    course_number = serializers.IntegerField(source='course.number', read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'number', 'course_number']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    current_semester = SemesterSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'full_name', 'group',
            'department', 'current_semester', 'year_of_entry',
            'is_student', 'is_staff_member',
        ]
