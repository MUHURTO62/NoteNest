from rest_framework import serializers
from .models import (
    User,
    Semester,
    Course,
    QuestionPaper,
    Faculty,
    Bookmark,
    ActivityLog,
    Comment,
    NoteUploadRequest,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'student_id', 'email', 'role', 'date_joined']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'credit_hours', 'prerequisite']


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'number', 'label', 'courses']


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'position', 'email', 'created_at']


class QuestionPaperSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    semester_number = serializers.IntegerField(source='semester.number', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.student_id', read_only=True, default=None)
    question_file_url = serializers.SerializerMethodField()

    class Meta:
        model = QuestionPaper
        fields = [
            'id', 'semester', 'course', 'year', 'session', 'term', 'drive_link', 'question_file',
            'question_file_url', 'description', 'uploaded_by', 'uploaded_at',
            'course_code', 'course_name', 'semester_number', 'uploaded_by_name',
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at', 'question_file_url']

    def get_question_file_url(self, obj):
        if obj.question_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.question_file.url)
            return obj.question_file.url
        return ''


class QuestionPaperCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a question paper."""

    class Meta:
        model = QuestionPaper
        fields = ['id', 'semester', 'course', 'year', 'session', 'term', 'drive_link', 'question_file', 'description']

    def validate(self, data):
        if not data.get('drive_link') and not data.get('question_file'):
            raise serializers.ValidationError('Please provide either a drive link or upload a PDF file.')
        return data


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['student_id', 'email', 'password', 'security_question', 'security_answer']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['student_id'],
            student_id=validated_data['student_id'],
            email=validated_data['email'],
            password=validated_data['password'],
            security_question=validated_data.get('security_question', ''),
            security_answer=validated_data.get('security_answer', ''),
            role='student'
        )
        return user


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.student_id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'question_paper', 'content', 'created_at']
        read_only_fields = ['user', 'user_name', 'created_at']


class NoteUploadRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.student_id', read_only=True)
    note_file_url = serializers.SerializerMethodField()

    class Meta:
        model = NoteUploadRequest
        fields = [
            'id', 'user', 'user_name', 'title', 'description', 'note_file', 'note_file_url',
            'status', 'admin_message', 'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'user_name', 'note_file_url', 'created_at', 'updated_at']

    def get_note_file_url(self, obj):
        if obj.note_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.note_file.url)
            return obj.note_file.url
        return ''


class BookmarkSerializer(serializers.ModelSerializer):
    question_paper_details = QuestionPaperSerializer(source='question_paper', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'question_paper', 'question_paper_details', 'created_at']
        read_only_fields = ['user', 'created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'timestamp']
        read_only_fields = ['user', 'timestamp']
