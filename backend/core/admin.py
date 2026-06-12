# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Semester, Course, QuestionPaper, Faculty, Bookmark, ActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['student_id', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['student_id', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('NoteNest Fields', {'fields': ('student_id', 'role', 'security_question', 'security_answer')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('NoteNest Fields', {'fields': ('student_id', 'email', 'role')}),
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['number', 'label']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credit_hours', 'semester', 'prerequisite']
    list_filter = ['semester']
    search_fields = ['code', 'name']


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ['course', 'semester', 'year', 'session', 'term', 'uploaded_by', 'uploaded_at']
    list_filter = ['semester', 'year', 'session', 'term']
    search_fields = ['course__code', 'course__name']


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'email']
    list_filter = ['position']
    search_fields = ['name', 'email']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_paper', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__student_id', 'question_paper__course__code']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'user__student_id', 'action']
