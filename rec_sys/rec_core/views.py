from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, generics, serializers
from rest_framework import viewsets, filters

from django.utils.timezone import now
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.generics import ListAPIView
from django.utils import timezone
from django.db import transaction

from django.http import JsonResponse
from django.db.models import Q

from .recommender import recommend_for
from .models import ( Faculty, Department, Course, Subject, Tag, Questionnaire, TaskProgress, ModuleProgress, 
                     ResearchProgress, Recommendation, RecommendationHistory, EBook, Task )

from .serializers import ( UserSerializer, MyTokenObtainPairSerializer, FacultySerializer, DepartmentSerializer, 
                          CourseSerializer, SubjectSerializer, TagSerializer, SubjectWithModulesSerializer,
                          ModuleSerializer, TaskProgressSerializer, TaskSerializer, ModuleProgressUpdateSerializer,
                          TaskProgressUpdateSerializer, ResearchProgressSerializer, EBookSerializer, RecommendationSerializer,
                          RecommendationHistorySerializer, DeadlineTaskSerializer
                          )

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
    
import logging
logger = logging.getLogger(__name__)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_questionnaire(request):
    logger.info("Вызов save_questionnaire")
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

    print("Перед вызовом recommend_for1")
    books = recommend_for(user, top_k=3)
    if books:
        book = books[0] if isinstance(books, list) else books
        # либо update, либо create
        rec, _ = Recommendation.objects.update_or_create(
            student=user,
            defaults={"book": book}
        )
        # историю пишем отдельной записью
        RecommendationHistory.objects.create(
            student = user,
            title   = book.title,
           author  = book.author,
           link    = book.link
       )

        # можно вернуть саму рекомендацию сразу
        
        return Response(RecommendationSerializer(rec).data, status=200)

    # если подобрать нечего – очищаем текущую
    Recommendation.objects.filter(student=user).delete()
    print("Рекомендация: ", RecommendationSerializer(rec).data)
    return Response({}, status=200)


class StudentGradesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user

        # Получаем предметы с модулями (как раньше)
        subjects = Subject.objects.filter(
            semester=student.current_semester,
            department=student.department
        ).distinct()

        subjects_data = SubjectWithModulesSerializer(subjects, many=True, context={'student': student}).data

        # Получаем прогресс по НИР для текущего семестра и студента
        research_progress_qs = ResearchProgress.objects.filter(student=student, semester=student.current_semester)
        research_data = ResearchProgressSerializer(research_progress_qs, many=True).data

        return Response({
            "subjects": subjects_data,
            "research": research_data
        })
    
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
    
# views.py
class ModuleProgressUpdateView(generics.UpdateAPIView):
    queryset           = ModuleProgress.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names  = ['patch']

    class InputSerializer(serializers.Serializer):
        score = serializers.IntegerField(min_value=0)

    def patch(self, request, pk):
        try:
            mp = ModuleProgress.objects.get(pk=pk, student=request.user)
        except ModuleProgress.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = self.InputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # не даём ввести больше, чем max_score
        max_score = mp.module.max_score
        mp.score  = min(ser.validated_data['score'], max_score)
        mp.save()
        return Response({"status": "updated", "score": mp.score, "max_score": max_score})


class SaveProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student = request.user
        data = request.data  # ожидаем список прогрессов модулей

        # data = [{id: ..., score: ..., tasks_progress: [{id:..., is_completed:...}, ...]}, ...]

        for module_progress_data in data:
            module_progress_id = module_progress_data.get('id')
            try:
                module_progress = ModuleProgress.objects.get(id=module_progress_id, student=student)
            except ModuleProgress.DoesNotExist:
                continue  # либо возвращать ошибку

            serializer = ModuleProgressUpdateSerializer(
                module_progress,
                data=module_progress_data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({"detail": "Прогресс сохранён"}, status=status.HTTP_200_OK)
    
class EBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EBook.objects.all().order_by('title')  # сортировка по алфавиту
    serializer_class = EBookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['author', 'title']  # Здесь указываем поля для поиска
    

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print("Перед вызовом recommend_for22")
        books = recommend_for(user, top_k=5)  # предположим, это queryset или список EBook

        # Создаём рекомендации и историю атомарно
        with transaction.atomic():
            rec_objs = []
            history_objs = []
            for book in books:
                rec = Recommendation.objects.create(book=book, student=user)
                rec_objs.append(rec)
                history_objs.append(
                    RecommendationHistory(student=user, recommendation=rec)
                )
            # Создаём все записи истории одним запросом
            RecommendationHistory.objects.bulk_create(history_objs)

        # Возвращаем книги, сериализуем их так, как раньше
        return Response(EBookSerializer(books, many=True).data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_recommendation(request):
    user = request.user
    rec = Recommendation.objects.filter(student=user).order_by('-created_at').first()
    if not rec:
        return Response({"detail": "No recommendations found"}, status=404)
    serializer = RecommendationSerializer(rec)
    return Response(serializer.data)

class LatestRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        latest_rec = Recommendation.objects.filter(student=user).order_by('-created_at').first()
        if not latest_rec:
            return Response({}, status=200)


        serializer = RecommendationSerializer(latest_rec)
        print("Рекомендация: ",serializer.data)
        return Response(serializer.data)
    
    
class RecommendationHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationHistorySerializer

    def get_queryset(self):
        # берём всю историю текущего пользователя, в порядке убывания даты
        return RecommendationHistory.objects.filter(
            student=self.request.user
        ).order_by('-created_at')
        
        
class DeadlinesAPIView(generics.ListAPIView):
    serializer_class = DeadlineTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        today = now()
        return Task.objects.filter(deadline__gte=today).order_by('deadline')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context