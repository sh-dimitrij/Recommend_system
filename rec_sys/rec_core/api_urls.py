from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    login_view, UserView, MyTokenObtainPairView, FacultyListView,
    DepartmentListView, CourseListView, SubjectListAPIView, TagListAPIView,
    save_questionnaire, StudentGradesView, TaskProgressUpdateView,
    ModuleProgressUpdateView, SaveProgressAPIView, RecommendationView,
    LatestRecommendationView, RecommendationHistoryListView, EBookViewSet,
    DeadlinesAPIView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'ebooks', EBookViewSet, basename='ebooks')

urlpatterns = [
    
    path('deadlines/', DeadlinesAPIView.as_view(), name='deadlines-list'),
    path('student-grades/', StudentGradesView.as_view(), name='student-grades'),
    path('history/', RecommendationHistoryListView.as_view(), name='history'),
    
    path('recommendation/latest/', LatestRecommendationView.as_view(), name='latest_recommendation'),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    
    path('save-progress/', SaveProgressAPIView.as_view(), name='save-progress'),
    path('module-progress/<int:pk>/', ModuleProgressUpdateView.as_view()),
    path('task-progress/<int:pk>/', TaskProgressUpdateView.as_view(), name='task-progress-update'),
    path('questionnaire/save/', save_questionnaire, name='save_questionnaire'),
    
    path("tags/", TagListAPIView.as_view(), name="tag-list"),
    path('subjects/', SubjectListAPIView.as_view(), name='subject-list'),
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('faculties/', FacultyListView.as_view(), name='faculty-list'),
    
    path('user/', UserView.as_view(), name='user'),
    path('login/', login_view, name='login'),
    
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # подключаем router через include
    path('', include(router.urls)),
]
