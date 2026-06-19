from django.urls import path
from . import views

urlpatterns = [
    # Admin & Shared Data Endpoints
    path('overview/', views.AdminOverviewView.as_view(), name='admin-overview'),
    path('users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('faculty/', views.AdminFacultyListCreateView.as_view(), name='admin-faculty-list'),
    path('faculty/<int:pk>/', views.AdminFacultyDeleteView.as_view(), name='admin-faculty-delete'),
    path('questions/', views.AdminQuestionListCreateView.as_view(), name='admin-questions-list'),
    path('questions/<int:pk>/', views.AdminQuestionDeleteView.as_view(), name='admin-questions-delete'),
    path('questions/<int:question_paper_id>/comments/', views.QuestionCommentListCreateView.as_view(), name='question-comments'),
    path('semesters/', views.SemesterListView.as_view(), name='admin-semesters'),

    # Auth Endpoints
    path('auth/signup/', views.SignupView.as_view(), name='auth-signup'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/me/', views.UserMeView.as_view(), name='auth-me'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('auth/reset-password/', views.ResetPasswordView.as_view(), name='auth-reset-password'),
    path('auth/request-reset-code/', views.RequestPasswordResetCodeView.as_view(), name='auth-request-reset-code'),
    path('auth/verify-reset-code/', views.VerifyPasswordResetCodeView.as_view(), name='auth-verify-reset-code'),

    # Student Endpoints
    path('student/bookmarks/', views.BookmarkListCreateView.as_view(), name='student-bookmarks'),
    path('student/bookmarks/<int:question_paper_id>/', views.BookmarkDeleteView.as_view(), name='student-bookmark-delete'),
    path('student/history/', views.ActivityLogListView.as_view(), name='student-history'),
    path('student/log-view/', views.LogQuestionView.as_view(), name='student-log-view'),
    path('student/note-requests/', views.NoteUploadRequestListCreateView.as_view(), name='student-note-requests'),
    path('admin/note-requests/', views.AdminNoteRequestListView.as_view(), name='admin-note-requests'),
    path('admin/note-requests/<int:pk>/', views.AdminNoteRequestUpdateView.as_view(), name='admin-note-request-update'),
]
