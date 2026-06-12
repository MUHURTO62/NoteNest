from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with student-specific fields."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]

    student_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    security_question = models.CharField(max_length=255, blank=True, default='')
    security_answer = models.CharField(max_length=255, blank=True, default='')

    # Make email required and unique
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.student_id} ({self.role})"


class Semester(models.Model):
    """Represents a semester (1-8)."""
    number = models.IntegerField(unique=True)
    label = models.CharField(max_length=50)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.label


class Course(models.Model):
    """A course belonging to a semester."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credit_hours = models.FloatField()
    prerequisite = models.CharField(max_length=20, default='-')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class QuestionPaper(models.Model):
    """An uploaded question paper with a Google Drive link."""
    YEAR_CHOICES = [
        ('26', '2026'),
        ('25', '2025'),
        ('24', '2024'),
        ('23', '2023'),
        ('22', '2022'),
    ]
    SESSION_CHOICES = [
        ('Autumn', 'Autumn'),
        ('Spring', 'Spring'),
    ]
    TERM_CHOICES = [
        ('Mid', 'Mid'),
        ('Final', 'Final'),
    ]

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='questions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    year = models.CharField(max_length=4, choices=YEAR_CHOICES, default='25')
    session = models.CharField(max_length=10, choices=SESSION_CHOICES, default='Autumn')
    term = models.CharField(max_length=10, choices=TERM_CHOICES, default='Mid')
    drive_link = models.URLField()
    description = models.TextField(blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.course.code} - {self.session} {self.year} ({self.term})"


class Faculty(models.Model):
    """A faculty member of the CSE department."""
    POSITION_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
    ]

    name = models.CharField(max_length=200)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.position})"


class Bookmark(models.Model):
    """A question paper bookmarked by a student/user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question_paper')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.student_id} bookmarked {self.question_paper}"


class ActivityLog(models.Model):
    """Logs of activities performed by users/students."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.student_id} - {self.action} at {self.timestamp}"
