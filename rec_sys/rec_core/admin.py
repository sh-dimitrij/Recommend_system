from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Faculty, Department, Course, Semester,
    Subject, Module, TaskType, Task, Tag,
    Questionnaire, ModuleProgress, TaskProgress,
    EBook,
    # Раскомментируй эти модели, если хочешь их добавить в админку
    # Recommendation, RecommendationHistory, Notification
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "full_name", "group", "department", "current_semester", "year_of_entry", "is_staff")
    list_filter = ("is_staff", "department", "current_semester")
    search_fields = ("username", "full_name", "group")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Личная информация", {
            "fields": ("full_name", "group", "department", "current_semester", "year_of_entry")
        }),
        ("Права доступа", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "password1", "password2",
                "full_name", "group", "department", "current_semester", "year_of_entry",
                "is_staff", "is_superuser", "is_active", "groups"
            ),
        }),
    )

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")
    search_fields = ("name", "short_name")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "faculty")
    list_filter = ("faculty",)
    search_fields = ("name", "short_name")

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("number",)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("number", "course")
    list_filter = ("course",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "semester", "is_exam")
    list_filter = ("department", "semester", "is_exam")
    search_fields = ("name",)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("subject", "number", "max_score")
    list_filter = ("subject",)
    search_fields = ("subject__name",)

@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "name")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("type", "get_binding", "deadline")
    list_filter = ("type", "deadline")
    search_fields = ("module__subject__name", "semester__course__number")

    def get_binding(self, obj):
        if obj.module:
            return f"Модуль: {obj.module}"
        elif obj.semester:
            return f"НИР: {obj.semester}"
        return "Не указано"
    get_binding.short_description = "Привязка"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("student", "faculty", "department", "course", "subject","free_time", "difficulty_level")
    list_filter = ("faculty", "department", "course", "difficulty_level")
    search_fields = ("student__username", "faculty", "department", "course")
    
    # Чтобы все поля были видны и редактируемы
    fields = (
        "student",
        "faculty",
        "department",
        "course",
        "subject",
        "free_time",
        "difficulty_level",
        "interest_tags",
    )
    
    filter_horizontal = ("interest_tags",)  # удобный виджет для ManyToMany


# Если захочешь добавить эти модели в админку, раскомментируй и настрой как нужно:
# @admin.register(StudentProgress)
# class StudentProgressAdmin(admin.ModelAdmin):
#     list_display = ("student", "module", "total_score")
#     search_fields = ("student__username", "module__number")

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'score')
    search_fields = ("student__username", "module__subject__name")

@admin.register(TaskProgress)
class TaskProgressAdmin(admin.ModelAdmin):
    list_display = ("module_progress", "task", "is_completed")
    list_filter = ("is_completed",)
    search_fields = ("module_progress__student_progress__student__username", "task__module__subject__name")

@admin.register(EBook)
class EBookAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    search_fields = ("title", "author")
    filter_horizontal = ("tags",)

# @admin.register(Recommendation)
# class RecommendationAdmin(admin.ModelAdmin):
#     list_display = ("book", "student", "created_at")
#     search_fields = ("book__title", "student__username")
#     list_filter = ("created_at",)

# @admin.register(RecommendationHistory)
# class RecommendationHistoryAdmin(admin.ModelAdmin):
#     list_display = ("student", "recommendation")
#     search_fields = ("student__username", "recommendation__book__title")

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ("student", "task", "created_at")
#     list_filter = ("created_at",)
#     search_fields = ("student__username", "task__module__subject__name")
