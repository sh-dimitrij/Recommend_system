from rest_framework import serializers
from .models import ( CustomUser, Department, Faculty, Course, Semester, Subject, Tag, Questionnaire,
                     Task, Module, ModuleProgress, TaskProgress)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth import authenticate

# Сериализатор кафедры с полями name и short_name
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name', 'short_name')

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'short_name']
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'number']
        
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'number']
        
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = [
            "faculty", "department", "course", "subject",
            "free_time", "difficulty_level", "interest_tags"
        ]




class UserSerializer(serializers.ModelSerializer):
    # Вместо SerializerMethodField теперь вложенный сериализатор
    department = DepartmentSerializer()

    course = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'full_name', 'group', 'department', 'course', 'semester', 'year_of_entry')

    def get_course(self, obj):
        return obj.course.number if obj.course else None

    def get_semester(self, obj):
        return obj.current_semester.number if obj.current_semester else None

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class MyTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Неверные логин или пароль")

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class TaskSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()  # например, "РК", "ДЗ", "ЛР"
    class Meta:
        model = Task
        fields = ['id', 'type', 'deadline']

class TaskProgressSerializer(serializers.ModelSerializer):
    task = TaskSerializer()
    class Meta:
        model = TaskProgress
        fields = ['task', 'is_completed']

class ModuleSerializer(serializers.ModelSerializer):
    tasks_progress = serializers.SerializerMethodField()
    max_score = serializers.IntegerField()
    number = serializers.IntegerField()
    
    class Meta:
        model = Module
        fields = ['id', 'number', 'max_score', 'tasks_progress']

    def get_tasks_progress(self, module):
        student = self.context['student']
        try:
            module_progress = ModuleProgress.objects.get(student=student, module=module)
        except ModuleProgress.DoesNotExist:
            return []
        task_progress_qs = TaskProgress.objects.filter(module_progress=module_progress).order_by('task__deadline')
        return TaskProgressSerializer(task_progress_qs, many=True).data

class SubjectWithModulesSerializer(serializers.ModelSerializer):
    modules = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'modules']

    def get_modules(self, subject):
        modules = Module.objects.filter(subject=subject).order_by('number')
        return ModuleSerializer(modules, many=True, context=self.context).data
