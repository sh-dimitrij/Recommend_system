from rest_framework import serializers
from .models import ( CustomUser, Department, Faculty, Course, Semester, Subject, Tag, Questionnaire,
                     Task, Module, ModuleProgress, TaskProgress, ResearchProgress, EBook, Recommendation,
                     RecommendationHistory
                     )
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


class RecommendationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = RecommendationHistory
        fields = ['id', 'title', 'author', 'link', 'created_at']


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
    id = serializers.IntegerField(source='pk')  # 👈 добавить это
    task = TaskSerializer()

    class Meta:
        model = TaskProgress
        fields = ['id', 'task', 'is_completed']

class RecommendationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = RecommendationHistory
        fields = ['id', 'student', 'title', 'author', 'link', 'created_at']
        read_only_fields = fields

class ModuleSerializer(serializers.ModelSerializer):
    tasks_progress   = serializers.SerializerMethodField()
    score            = serializers.SerializerMethodField()
    module_progress_id = serializers.SerializerMethodField()   # 👈 понадобится фронту
    max_score        = serializers.IntegerField()
    number           = serializers.IntegerField()

    class Meta:
        model  = Module
        fields = [
            'id', 'number',
            'max_score',           # оставляем, чтобы показать «из 20»
            'score',               # пользовательский балл
            'module_progress_id',  # для PATCH-а
            'tasks_progress'
        ]

    # --- вспомогательная «ленивая» инициализация -----------------------------
    def _get_or_create_module_progress(self, module):
        student = self.context['student']
        mp, _ = ModuleProgress.objects.get_or_create(
            student = student,
            module  = module,
            defaults={'score': 0}
        )
        # создаём TaskProgress-ы под все задания модуля
        for task in Task.objects.filter(module=module):
            TaskProgress.objects.get_or_create(
                module_progress = mp,
                task            = task
            )
        return mp
    # --------------------------------------------------------------------------

    def get_tasks_progress(self, module):
        mp = self._get_or_create_module_progress(module)
        qs = TaskProgress.objects.filter(
            module_progress = mp
        ).order_by('task__deadline')
        return TaskProgressSerializer(qs, many=True).data

    def get_score(self, module):
        return self._get_or_create_module_progress(module).score

    def get_module_progress_id(self, module):
        return self._get_or_create_module_progress(module).id



class SubjectWithModulesSerializer(serializers.ModelSerializer):
    modules = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'modules']

    def get_modules(self, subject):
        modules = Module.objects.filter(subject=subject).order_by('number')
        return ModuleSerializer(modules, many=True, context=self.context).data
    
class TaskProgressUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # id TaskProgress

    class Meta:
        model = TaskProgress
        fields = ['id', 'is_completed']

class ModuleProgressUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # id ModuleProgress (для поиска)
    score = serializers.IntegerField()
    tasks_progress = TaskProgressUpdateSerializer(many=True)

    class Meta:
        model = ModuleProgress
        fields = ['id', 'score', 'tasks_progress']

    def update(self, instance, validated_data):
        # Обновляем score модуля
        instance.score = validated_data.get('score', instance.score)
        instance.save()

        # Обновляем задачи
        tasks_data = validated_data.get('tasks_progress', [])
        for task_data in tasks_data:
            task_progress_id = task_data.get('id')
            is_completed = task_data.get('is_completed')
            try:
                task_progress = TaskProgress.objects.get(id=task_progress_id, module_progress=instance)
                task_progress.is_completed = is_completed
                task_progress.save()
            except TaskProgress.DoesNotExist:
                pass  # Можно логировать или игнорировать

        return instance
    
class ResearchProgressSerializer(serializers.ModelSerializer):
    task_type = serializers.CharField(source='task.type.name')
    task_deadline = serializers.DateTimeField(source='task.deadline')

    class Meta:
        model = ResearchProgress
        fields = ['id', 'score', 'is_completed', 'task_type', 'task_deadline', 'task']
        
class EBookSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model  = EBook
        fields = ['id', 'title', 'author', 'difficulty_level', 'tags', 'link', 'views']


class RecommendationSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title')
    book_author = serializers.CharField(source='book.author')  # если у книги есть author
    book_link = serializers.CharField(source='book.link')  # или другой URL к книге

    class Meta:
        model = Recommendation
        fields = ['id', 'book_title', 'book_author', 'book_link', 'created_at']
        
        
class DeadlineTaskSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()  # "РК", "ДЗ", "ЛР"
    module = serializers.StringRelatedField()  # например, "М1 - Математика"
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'type', 'module', 'deadline', 'is_completed']

    def get_is_completed(self, obj):
        user = self.context.get('user')
        if not user:
            return False

        try:
            mp = ModuleProgress.objects.get(student=user, module=obj.module)
            tp = TaskProgress.objects.get(module_progress=mp, task=obj)
            return tp.is_completed
        except (ModuleProgress.DoesNotExist, TaskProgress.DoesNotExist):
            return False