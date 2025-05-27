from django.db import models
from django.contrib.auth.models import AbstractUser

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

    def __str__(self):
        return self.username

    @property
    def course(self):
        return self.current_semester.course if self.current_semester else None

    @property
    def semester_num(self):
        return self.current_semester.number if self.current_semester else None
    
    
class Subject(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    is_exam = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}"
    
class Module(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"М{self.number} - {self.subject.name}"
    class Meta:
        unique_together = ('subject', 'number')
        
class TaskType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return f"{self.name}"


class Task(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    deadline = models.DateTimeField()

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.module and not self.semester:
            raise ValidationError("Task должен быть привязан либо к модулю, либо к семестру.")
        if self.module and self.semester:
            raise ValidationError("Task не может быть одновременно привязан и к модулю, и к семестру.")

    def __str__(self):
        if self.module:
            return f"{self.type.name} ({self.module})"
        elif self.semester:
            return f"{self.type.name} (НИР, {self.semester})"
        return f"{self.type.name} (без привязки)"

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"

    
# class StudentProgress(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     module = models.ForeignKey(Module, on_delete=models.CASCADE)  # временно допускаем null
#     total_score = models.PositiveSmallIntegerField(default=0)

#     # class Meta:
#     #     unique_together = ('student', 'module')

        
class ModuleProgress(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'module')
        
class TaskProgress(models.Model):
    module_progress = models.ForeignKey(ModuleProgress, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('module_progress', 'task')

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class EBook(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)

# class Recommendation(models.Model):
#     book = models.ForeignKey(EBook, on_delete=models.CASCADE)
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

# class RecommendationHistory(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)

# class Notification(models.Model):
#     student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

class Questionnaire(models.Model):
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Начинающий'),
        ('INTERMEDIATE', 'Средний'),
        ('ADVANCED', 'Продвинутый'),
    ]

    student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='questionnaire')

    faculty = models.CharField(max_length=255, verbose_name="Факультет")
    department = models.CharField(max_length=255, verbose_name="Кафедра")
    course = models.CharField(max_length=255, verbose_name="Курс")

    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Предмет")

    free_time = models.PositiveSmallIntegerField(verbose_name="Свободное время (часов в неделю)", null=True, blank=True)

    difficulty_level = models.CharField(
        max_length=12,
        choices=DIFFICULTY_LEVELS,
        verbose_name="Уровень сложности",
        null=True, blank=True
    )

    interest_tags = models.ManyToManyField(Tag, verbose_name="Интересы (тэги)", blank=True)

    def __str__(self):
        return f"Анкета {self.student}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Форма"
        verbose_name_plural = "Формы"
