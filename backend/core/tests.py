from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from core.models import User, Semester, Course, Faculty, QuestionPaper, Bookmark, ActivityLog


class NoteNestBackendTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            student_id='ADMIN-100',
            email='admin@test.com',
            password='testpassword',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='student_user',
            student_id='CSE-100',
            email='student@test.com',
            password='testpassword',
            role='student',
            security_question='What is your pet name?',
            security_answer='Rocky'
        )

        # Create base models
        self.semester = Semester.objects.create(number=1, label='1st Semester')
        self.course = Course.objects.create(
            code='CSE-1121',
            name='Computer Programming I',
            credit_hours=3.0,
            prerequisite='-',
            semester=self.semester
        )
        self.faculty = Faculty.objects.create(
            name='Dr. Test',
            position='Professor',
            email='test@iiuc.ac.bd'
        )
        self.question = QuestionPaper.objects.create(
            semester=self.semester,
            course=self.course,
            year='24',
            session='Autumn',
            term='Mid',
            drive_link='https://drive.google.com/test',
            uploaded_by=self.admin_user
        )

    def test_model_str_methods(self):
        """Test the string representations of all models."""
        self.assertEqual(str(self.admin_user), "ADMIN-100 (admin)")
        self.assertEqual(str(self.semester), "1st Semester")
        self.assertEqual(str(self.course), "CSE-1121 - Computer Programming I")
        self.assertEqual(str(self.faculty), "Dr. Test (Professor)")
        self.assertEqual(str(self.question), "CSE-1121 - Autumn 24 (Mid)")

    def test_anonymous_access_permissions(self):
        """Verify anonymous access: semesters is allowed, others are blocked."""
        # Semesters is public (AllowAny)
        response = self.client.get(reverse('admin-semesters'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin/authenticated endpoints are blocked
        blocked_endpoints = [
            reverse('admin-overview'),
            reverse('admin-users'),
            reverse('admin-faculty-list'),
            reverse('admin-questions-list'),
        ]
        for url in blocked_endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_read_allowed_write_denied(self):
        """Verify students can read questions and faculty, but cannot write."""
        self.client.force_login(self.student_user)

        # 1. Accessing strict admin-only endpoints should be blocked
        admin_only = [reverse('admin-overview'), reverse('admin-users')]
        for url in admin_only:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. GET on shared endpoints is allowed
        self.assertEqual(self.client.get(reverse('admin-semesters')).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse('admin-faculty-list')).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse('admin-questions-list')).status_code, status.HTTP_200_OK)

        # 3. POST on shared endpoints is blocked for students
        new_faculty_data = {'name': 'No Student Write', 'position': 'Lecturer', 'email': 'ns@test.com'}
        self.assertEqual(self.client.post(reverse('admin-faculty-list'), new_faculty_data).status_code, status.HTTP_403_FORBIDDEN)

        new_question_data = {
            'semester': self.semester.id,
            'course': self.course.id,
            'term': 'Sp-25',
            'drive_link': 'https://drive.google.com/test'
        }
        self.assertEqual(self.client.post(reverse('admin-questions-list'), new_question_data).status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access_allowed(self):
        """Verify admin role requests succeed on all endpoints."""
        self.client.force_login(self.admin_user)
        
        response = self.client.get(reverse('admin-overview'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_users'], 2)
        self.assertEqual(response.data['total_questions'], 1)
        self.assertEqual(response.data['total_faculty'], 1)

        response = self.client.get(reverse('admin-users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('admin-faculty-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signup_and_login_api(self):
        """Test API endpoints for student signup and login."""
        # 1. Signup
        signup_data = {
            'student_id': 'CSE-999',
            'email': 'newstudent@test.com',
            'password': 'studentpassword123',
            'security_question': 'First pet name?',
            'security_answer': 'Buddy'
        }
        response = self.client.post(reverse('auth-signup'), signup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(student_id='CSE-999').count(), 1)

        # 2. Login
        login_data = {
            'identifier': 'CSE-999',
            'password': 'studentpassword123'
        }
        response = self.client.post(reverse('auth-login'), login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['studentId'], 'CSE-999')

    def test_forgot_and_reset_password(self):
        """Test password recovery using security questions."""
        # 1. Forgot password - Get security question
        response = self.client.get(reverse('auth-forgot-password'), {'identifier': 'student@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['security_question'], 'What is your pet name?')

        # 2. Reset password - incorrect answer
        reset_data_fail = {
            'identifier': 'student@test.com',
            'security_answer': 'WrongAnswer',
            'new_password': 'newpassword123'
        }
        response = self.client.post(reverse('auth-reset-password'), reset_data_fail)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Reset password - correct answer
        reset_data_success = {
            'identifier': 'student@test.com',
            'security_answer': 'Rocky',
            'new_password': 'newpassword123'
        }
        response = self.client.post(reverse('auth-reset-password'), reset_data_success)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify login with new password works
        login_response = self.client.post(reverse('auth-login'), {
            'identifier': 'student@test.com',
            'password': 'newpassword123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_student_bookmarks(self):
        """Test creating, listing, and deleting question paper bookmarks."""
        self.client.force_login(self.student_user)

        # 1. Create Bookmark
        response = self.client.post(reverse('student-bookmarks'), {'question_paper': self.question.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bookmark.objects.filter(user=self.student_user).count(), 1)

        # 2. List Bookmarks
        response = self.client.get(reverse('student-bookmarks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question_paper_details']['course_code'], 'CSE-1121')

        # 3. Delete Bookmark
        delete_url = reverse('student-bookmark-delete', kwargs={'question_paper_id': self.question.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bookmark.objects.filter(user=self.student_user).count(), 0)

    def test_student_activity_logging(self):
        """Test activity logging triggers on actions and displays in history."""
        self.client.force_login(self.student_user)

        # 1. Log a view action
        response = self.client.post(reverse('student-log-view'), {'question_paper': self.question.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Fetch history
        response = self.client.get(reverse('student-history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain "Viewed question paper" action
        actions = [log['action'] for log in response.data]
        self.assertTrue(any("Viewed question paper" in a for a in actions))
