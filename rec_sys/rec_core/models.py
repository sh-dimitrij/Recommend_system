from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime  # Добавьте эту строку вверху файла

class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Course(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return f"{self.number} курс"


class Semester(models.Model):
    number = models.PositiveSmallIntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('number', 'course')

    def __str__(self):
        return f"{self.number} семестр ({self.course})"


class CustomUser(AbstractUser):
    # Студенческие поля
    full_name = models.CharField(max_length=255)
    group = models.CharField(max_length=40)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    current_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    year_of_entry = models.PositiveIntegerField(null=True, blank=True)

    # Роли
    is_student = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)  # например, для сотрудников кафедры

    def __str__(self):
        return self.username

    @property
    def course(self):
        return self.current_semester.course if self.current_semester else None

    @property
    def semester(self):
        return self.current_semester.number if self.current_semester else None

    def __str__(self):
        return self.full_name or self.username


class Subject(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)  # добавлено
    has_coursework = models.BooleanField(default=False)
    has_research = models.BooleanField(default=False)
    has_labs = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Module(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100)
    max_score = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.subject.name} – Модуль {self.number}"


class Task(models.Model):
    TASK_TYPES = (
        ('rk', 'Рубежный контроль'),
        ('hw', 'Домашнее задание'),
        ('lab', 'Лабораторная работа'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TASK_TYPES)
    index = models.PositiveSmallIntegerField(null=True, blank=True)  # Например, 1, 2, 3 лаба
    max_score = models.PositiveSmallIntegerField()
    teacher_score = models.PositiveSmallIntegerField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        label = dict(self.TASK_TYPES).get(self.type, self.type)
        return f"{label} – {self.module}"


class Work(models.Model):
    WORK_TYPES = (
        ('coursework', 'Курсовая работа'),
        ('research',  'НИР'),
    )

    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=WORK_TYPES)

    # Курсовая — по предмету
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=True, blank=True)

    # НИР — по кафедре и семестру
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE, null=True, blank=True)

    # Общие поля
    title = models.CharField(max_length=255)
    max_score = models.PositiveSmallIntegerField()
    teacher_score = models.PositiveSmallIntegerField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.type == 'coursework':
            if not self.subject:
                raise ValidationError('Курсовая работа должна быть привязана к предмету.')
            if self.semester or self.department:
                raise ValidationError('Курсовая работа не должна быть привязана к семестру или кафедре.')

        elif self.type == 'research':
            if not self.department or not self.semester:
                raise ValidationError('НИР должен быть привязан к семестру и кафедре.')
            if self.subject:
                raise ValidationError('НИР не должен быть привязан к предмету.')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'type'],
                condition=models.Q(type='coursework'),
                name='unique_coursework_per_subject'
            ),
            models.UniqueConstraint(
                fields=['student', 'department', 'semester', 'type'],
                condition=models.Q(type='research'),
                name='unique_research_per_department_semester'
            ),
        ]

    def __str__(self):
        if self.type == 'coursework':
            return f"КР — {self.subject.name} ({self.student.full_name})"
        else:
            return f"НИР — {self.department.name}, {self.semester} ({self.student.full_name})"


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

        
class RecommendationHistory(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    books = models.ManyToManyField('Book')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Рекомендации для {self.student.full_name} от {self.created_at:%Y-%m-%d %H:%M}"
