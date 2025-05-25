from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
    
from .models import (
    Faculty, Department, Course, Semester, CustomUser,
    Subject, Module, Task, Work,
    Tag, Book, RecommendationHistory
)

# ========== Университет ==========
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'short_name')
    search_fields = ('name', 'short_name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'short_name', 'faculty')
    list_filter   = ('faculty',)
    search_fields = ('name', 'short_name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('id', 'number',)
    search_fields = ('number',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display  = ('id', 'number', 'course')
    list_filter   = ('course',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'full_name', 'group', 'department', 'year_of_entry', 'is_student', 'is_staff_member', 'is_staff', 'is_superuser')
    list_filter = ('department', 'current_semester__course', 'is_student', 'is_staff_member')
    search_fields = ('username', 'full_name', 'group')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'group', 'department', 'current_semester', 'year_of_entry')}),
        ('Permissions', {'fields': ('is_student', 'is_staff_member', 'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'full_name', 'group', 'department', 'current_semester', 'year_of_entry', 'is_student', 'is_staff_member', 'is_staff', 'is_superuser'),
        }),
    )



# ========== Учебный процесс ==========
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'department', 'semester', 'has_coursework', 'has_research', 'has_labs')
    list_filter   = ('department', 'semester__course')
    search_fields = ('name',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display  = ('id', 'subject', 'number', 'name', 'max_score')
    list_filter   = ('subject',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('id', 'type', 'index', 'module', 'max_score', 'teacher_score', 'deadline')
    list_filter   = ('type', 'module__subject__semester__course')
    search_fields = ('module__subject__name',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display  = ('id', 'type', 'title', 'student', 'subject', 'teacher_score', 'deadline')
    list_filter   = ('type', 'subject__semester__course')
    search_fields = ('title', 'student__full_name')


# ========== Материалы ==========
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'author', 'subject', 'module')
    list_filter   = ('subject__semester__course',)
    search_fields = ('title', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name',)
    search_fields = ('name',)


# ========== История рекомендаций ==========
@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display  = ('id', 'student', 'created_at')
    list_filter   = ('created_at',)
    date_hierarchy = 'created_at'
