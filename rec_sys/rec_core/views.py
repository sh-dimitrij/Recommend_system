from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, generics, serializers

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.generics import ListAPIView


from django.http import JsonResponse
from django.db.models import Q

from .models import Faculty, Department, Course, Subject, Tag, Questionnaire, TaskProgress
from .serializers import ( UserSerializer, MyTokenObtainPairSerializer, FacultySerializer, DepartmentSerializer, 
                          CourseSerializer, SubjectSerializer, TagSerializer, SubjectWithModulesSerializer,
                          ModuleSerializer, TaskProgressSerializer, TaskSerializer)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return JsonResponse({
                'success': True,
                'user': serializer.data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class FacultyListView(ListAPIView):
    queryset = Faculty.objects.all().order_by('name')
    serializer_class = FacultySerializer
    
class DepartmentListView(ListAPIView):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        faculty_name = self.request.GET.get("faculty", None)
        if faculty_name:
            return Department.objects.filter(faculty__name=faculty_name).order_by('name')
        return Department.objects.all().order_by('name')
    
class CourseListView(ListAPIView):
    queryset = Course.objects.all().order_by('number')
    serializer_class = CourseSerializer

class SubjectListAPIView(ListAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.all()
        faculty_name = self.request.GET.get("faculty", None)
        department_name = self.request.GET.get("department", None)
        course_number = self.request.GET.get("course", None)

        filters = {}
        if faculty_name:
            filters['department__faculty__name'] = faculty_name
        if department_name:
            filters['department__name'] = department_name
        if course_number:
            filters['semester__course__number'] = course_number

        if filters:
            queryset = queryset.filter(**filters)

        return queryset.order_by('name')
    
class TagListAPIView(ListAPIView):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_questionnaire(request):
    user = request.user
    data = request.data

    # Получаем или создаём анкету для пользователя
    questionnaire, created = Questionnaire.objects.get_or_create(student=user)

    # Заполняем поля из data
    questionnaire.faculty = data.get('faculty', '')
    questionnaire.department = data.get('department', '')
    questionnaire.course = str(data.get("course") or "")


    subject_id = data.get('subject')
    if subject_id:
        try:
            subject = Subject.objects.get(id=subject_id)
            questionnaire.subject = subject
        except Subject.DoesNotExist:
            questionnaire.subject = None
    else:
        questionnaire.subject = None

    questionnaire.free_time = data.get('free_time')
    
    difficulty_map = {
        'Начинающий': 'BEGINNER',
        'Средний': 'INTERMEDIATE',
        'Продвинутый': 'ADVANCED',
    }
    difficulty_level = data.get('difficulty_level')
    questionnaire.difficulty_level = difficulty_map.get(difficulty_level)

    questionnaire.save()

    # ManyToMany для тегов — очистим и добавим новые
    tag_ids = [i for i in data.get('interest_tags', []) if i]
    if tag_ids:
        tags = Tag.objects.filter(id__in=tag_ids)
        questionnaire.interest_tags.set(tags)
    else:
        questionnaire.interest_tags.clear()

    return Response({'status': 'ok'})


class StudentGradesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user
        # Получаем предметы студента: по его семестру и кафедре
        subjects = Subject.objects.filter(
            semester=student.current_semester,
            department=student.department
        ).distinct()

        serializer = SubjectWithModulesSerializer(subjects, many=True, context={'student': student})
        return Response(serializer.data)
    
class TaskProgressUpdateView(generics.UpdateAPIView):
    queryset = TaskProgress.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    # Можно создать простой сериализатор тут
    class InputSerializer(serializers.Serializer):
        is_completed = serializers.BooleanField()

    def patch(self, request, pk):
        try:
            task_progress = TaskProgress.objects.get(pk=pk, module_progress__student=request.user)
        except TaskProgress.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_progress.is_completed = serializer.validated_data['is_completed']
        task_progress.save()
        return Response({"status": "updated"})