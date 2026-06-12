from django.contrib.auth import authenticate
from rest_framework import generics, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Semester, Course, QuestionPaper, Faculty, Bookmark, ActivityLog
from .permissions import IsAdmin, IsAuthenticatedAndAdminOrReadOnly
from .serializers import (
    UserSerializer,
    SemesterSerializer,
    FacultySerializer,
    QuestionPaperSerializer,
    QuestionPaperCreateSerializer,
    UserSignupSerializer,
    BookmarkSerializer,
    ActivityLogSerializer,
)


# ─── Auth / User Views ───────────────────────────────────────────
class SignupView(generics.CreateAPIView):
    """POST /api/auth/signup/ — Register a new student account."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Log registration activity
        ActivityLog.objects.create(user=user, action="Registered account")


class LoginView(APIView):
    """POST /api/auth/login/ — Login with student ID or email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({'error': 'Please provide both identifier and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using email or student ID
        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = User.objects.get(student_id=identifier)
            except User.DoesNotExist:
                pass

        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            # Log login activity
            ActivityLog.objects.create(user=user, action="Logged in")
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'studentId': user.student_id,
                    'email': user.email,
                    'role': user.role,
                }
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserMeView(APIView):
    """GET /api/auth/me/ — Get currently authenticated user details."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'studentId': user.student_id,
            'email': user.email,
            'role': user.role,
            'security_question': user.security_question,
        })


class ForgotPasswordView(APIView):
    """GET /api/auth/forgot-password/?identifier=<student_id_or_email> — Fetch security question."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        identifier = request.query_params.get('identifier')
        if not identifier:
            return Response({'error': 'Identifier parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(student_id=identifier).first()

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.security_question:
            return Response({'error': 'No security question set for this account.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'student_id': user.student_id,
            'security_question': user.security_question,
        })


class ResetPasswordView(APIView):
    """POST /api/auth/reset-password/ — Reset password using correct answer to security question."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        security_answer = request.data.get('security_answer')
        new_password = request.data.get('new_password')

        if not identifier or not security_answer or not new_password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(student_id=identifier).first()

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.security_answer.strip().lower() == security_answer.strip().lower():
            user.set_password(new_password)
            user.save()
            ActivityLog.objects.create(user=user, action="Reset password via security question")
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Incorrect answer to the security question'}, status=status.HTTP_400_BAD_REQUEST)


# ─── Admin Overview ──────────────────────────────────────────────
class AdminOverviewView(APIView):
    """GET /api/admin/overview/ — Dashboard stats."""
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'total_questions': QuestionPaper.objects.count(),
            'total_faculty': Faculty.objects.count(),
            'total_semesters': Semester.objects.count(),
        })


# ─── Users ───────────────────────────────────────────────────────
class AdminUserListView(generics.ListAPIView):
    """GET /api/admin/users/ — List all users."""
    permission_classes = [IsAdmin]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


# ─── Faculty ─────────────────────────────────────────────────────
class AdminFacultyListCreateView(generics.ListCreateAPIView):
    """GET /api/admin/faculty/ — List all faculty (authenticated students/admins).
       POST /api/admin/faculty/ — Add a new faculty member (admin only)."""
    permission_classes = [IsAuthenticatedAndAdminOrReadOnly]
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class AdminFacultyDeleteView(generics.DestroyAPIView):
    """DELETE /api/admin/faculty/<id>/ — Delete a faculty member."""
    permission_classes = [IsAdmin]
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


# ─── Question Papers ─────────────────────────────────────────────
class AdminQuestionListCreateView(generics.ListCreateAPIView):
    """GET /api/admin/questions/ — List question papers with filtering (authenticated students/admins).
       POST /api/admin/questions/ — Upload a new question paper (admin only)."""
    permission_classes = [IsAuthenticatedAndAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionPaperCreateSerializer
        return QuestionPaperSerializer

    def get_queryset(self):
        queryset = QuestionPaper.objects.all()
        semester = self.request.query_params.get('semester')
        course_code = self.request.query_params.get('course')
        year = self.request.query_params.get('year')
        session = self.request.query_params.get('session')
        term = self.request.query_params.get('term')

        if semester:
            queryset = queryset.filter(semester__number=semester)
        if course_code:
            queryset = queryset.filter(course__code=course_code)
        if year:
            queryset = queryset.filter(year=year)
        if session:
            queryset = queryset.filter(session=session)
        if term:
            queryset = queryset.filter(term=term)
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class AdminQuestionDeleteView(generics.DestroyAPIView):
    """DELETE /api/admin/questions/<id>/ — Delete a question paper."""
    permission_classes = [IsAdmin]
    queryset = QuestionPaper.objects.all()
    serializer_class = QuestionPaperSerializer


# ─── Semesters (with courses for dropdowns & public subjects list) ──────────────────────
class SemesterListView(generics.ListAPIView):
    """GET /api/admin/semesters/ — List all semesters with their courses (AllowAny)."""
    permission_classes = [permissions.AllowAny]
    queryset = Semester.objects.prefetch_related('courses').all()
    serializer_class = SemesterSerializer


# ─── Student Bookmarks & Activity Logging ────────────────────────
class BookmarkListCreateView(APIView):
    """GET /api/student/bookmarks/ — List student bookmarks.
       POST /api/student/bookmarks/ — Bookmark a question paper."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    def post(self, request):
        question_paper_id = request.data.get('question_paper')
        if not question_paper_id:
            return Response({'error': 'Question paper ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qp = QuestionPaper.objects.get(id=question_paper_id)
        except QuestionPaper.DoesNotExist:
            return Response({'error': 'Question paper not found'}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, question_paper=qp)
        if created:
            ActivityLog.objects.create(user=request.user, action=f"Bookmarked question paper: {qp.course.code} ({qp.term})")
            return Response(BookmarkSerializer(bookmark).data, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already bookmarked'}, status=status.HTTP_200_OK)


class BookmarkDeleteView(APIView):
    """DELETE /api/student/bookmarks/<question_paper_id>/ — Delete a bookmark."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, question_paper_id):
        try:
            bookmark = Bookmark.objects.get(user=request.user, question_paper_id=question_paper_id)
            ActivityLog.objects.create(user=request.user, action=f"Removed bookmark for: {bookmark.question_paper.course.code} ({bookmark.question_paper.term})")
            bookmark.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Bookmark.DoesNotExist:
            return Response({'error': 'Bookmark not found'}, status=status.HTTP_404_NOT_FOUND)


class ActivityLogListView(generics.ListAPIView):
    """GET /api/student/history/ — List recent activities for logged in user."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')


class LogQuestionView(APIView):
    """POST /api/student/log-view/ — Log that user viewed/downloaded a question paper."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question_paper_id = request.data.get('question_paper')
        if not question_paper_id:
            return Response({'error': 'Question paper ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qp = QuestionPaper.objects.get(id=question_paper_id)
        except QuestionPaper.DoesNotExist:
            return Response({'error': 'Question paper not found'}, status=status.HTTP_404_NOT_FOUND)

        ActivityLog.objects.create(user=request.user, action=f"Viewed question paper: {qp.course.code} ({qp.term})")
        return Response({'message': 'Logged successfully'}, status=status.HTTP_200_OK)
