# NoteNest — Quick-Start Handbook

> A beginner-friendly guide to every file, every concept, and every data flow in the NoteNest project.
> Written for someone who knows basic Python and has heard of Django but has never built a real project.

---

## Table of Contents

1. [Big picture](#part-1--big-picture-read-this-first)
2. [Project structure](#part-2--project-structure)
3. [Backend files explained](#part-3--backend-files-explained)
4. [Frontend files explained](#part-4--frontend-files-explained)
5. [Django concepts for beginners](#part-5--django-concepts-for-beginners)
6. [How data flows through the app](#part-6--how-data-flows-through-the-whole-app)
7. [Deployment explained](#part-7--deployment-explained)
8. [Glossary](#part-8--glossary)

---

## PART 1 — Big picture (read this first)

### What is NoteNest?

NoteNest is a student-focused question bank for a university computer science department. It stores previous exam papers, faculty data, semester course lists, and student bookmarks. Students can browse subjects, log in, and access question papers without needing a full app install.

### What problem does it solve?

Instead of searching many places for study materials, students get one organized place for:

- Semester courses
- Faculty information
- Question papers
- Personal bookmarks
- Login and activity history

### What are the two main pieces?

| Piece | Location | What it does |
|-------|----------|--------------|
| Frontend | `frontend/` | The user interface — HTML, CSS, JavaScript |
| Backend | `backend/` | The API server — Django stores data and returns JSON |

They communicate like this:

```
Browser
   ↓  opens index.html
Frontend (HTML / CSS / JavaScript)
   ↓  sends HTTP requests (fetch)
Backend (Django REST API)
   ↓  queries
Database (SQLite locally, PostgreSQL on Render)
```

### What happens when a student opens the website and logs in?

1. The browser loads `index.html` and `script.js`.
2. JavaScript calls the backend API for semester and course data and shows it on the page.
3. The student clicks **Login** and enters their email or student ID plus password.
4. JavaScript sends a `POST` request to `/api/admin/auth/login/`.
5. Django checks the credentials and returns a token if they are valid.
6. The frontend stores the token and uses it for all future requests so the user stays logged in.

> **What you just learned:** NoteNest is a web app with a static browser frontend and a Django backend API. The frontend shows pages and asks the backend for data. The backend saves data in a database, checks passwords, and returns JSON.

---

## PART 2 — Project structure

```
NoteNest/
├── .env.example          → Template showing which environment variables are required.
├── .gitignore            → Files Git should ignore (secrets, cache, etc.)
├── build.sh              → Shell script run during deployment on Render.
├── Procfile              → Tells Render how to start the app.
├── README.md             → Project overview and setup instructions.
├── render.yaml           → Render deployment configuration.
├── requirements.txt      → Python dependencies list.
├── runtime.txt           → Python version to use on Render.
├── test_api.ps1          → PowerShell script for API testing.
├── User_Manual.md        → User-facing manual for students and admins.
│
├── frontend/
│   ├── index.html        → The main web page. Without it, there is no UI.
│   ├── script.js         → All JavaScript logic and API calls. Without it, buttons do nothing.
│   └── style.css         → All colours and layout rules. Without it, the page looks broken.
│
└── backend/
    ├── db.sqlite3        → Local SQLite database file (development only).
    ├── manage.py         → Django's command-line utility for running the server, migrations, etc.
    ├── requirements.txt  → Backend-specific dependencies.
    │
    ├── notenest_project/
    │   ├── settings.py   → Main Django configuration. Without it, Django cannot start.
    │   ├── urls.py       → Top-level URL routing. Without it, no requests reach any view.
    │   ├── wsgi.py       → Production server entry point used by Gunicorn.
    │   └── asgi.py       → Async server entry point (for future async support).
    │
    └── core/
        ├── models.py         → Database table definitions. Without it, there is no data structure.
        ├── views.py          → API request handlers. Without it, endpoints return nothing.
        ├── serializers.py    → Converts Django objects to/from JSON.
        ├── urls.py           → Routes core API URLs to views.
        ├── admin.py          → Django admin panel configuration.
        ├── permissions.py    → Custom access rules (who can do what).
        ├── apps.py           → Registers the core app with Django.
        ├── tests.py          → Automated tests.
        ├── management/
        │   └── commands/
        │       └── seed_data.py  → Fills the database with sample data.
        └── migrations/
            ├── 0001_initial.py              → Creates the first set of database tables.
            └── 0002_activitylog_bookmark.py → Adds bookmarks and activity logs.
```

> **What you just learned:** This project has a frontend folder for the browser and a backend folder for Django. Every file has a clear purpose: user interface, API logic, data models, deployment, or documentation.

---

## PART 3 — Backend files explained

---

### `manage.py`

**What is this file?**
Django's command-line utility. Think of it as the remote control for your Django project. It lets you start the server, run database migrations, and run tests.

**Key code:**

```python
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
```

> **WHAT IT DOES:** Finds the project root and adds it to Python's import path.
> **WHY IT IS HERE:** So Python can import Django modules from the correct location.
> **BEGINNER TIP:** Use `python manage.py runserver` to start the local development server.

---

### `settings.py`

**What is this file?**
The main configuration for the Django project. Like the Settings app on your phone — it controls how everything behaves.

**Key sections:**

```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-...')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [
    'notenest-1-auxz.onrender.com',
    'localhost',
    '127.0.0.1',
]
```

> **WHAT IT DOES:** Sets the secret key, debug mode, and allowed hosts.
> **WHY IT IS HERE:** `SECRET_KEY` encrypts sessions. `DEBUG=False` hides error details in production. `ALLOWED_HOSTS` stops unknown domains from reaching your app.
> **BEGINNER TIP:** Never run `DEBUG=True` in production — it exposes your database structure and source code to anyone who triggers an error.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'core',
]
```

> **WHAT IT DOES:** Lists every app Django should activate.
> **WHY IT IS HERE:** Django ignores apps not listed here — their models won't create tables, their URLs won't work.
> **BEGINNER TIP:** Always add new apps to this list after creating them.

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

> **WHAT IT DOES:** Defines code that runs on every single request, in order.
> **WHY IT IS HERE:** Handles security, sessions, CORS, authentication, and CSRF.
> **BEGINNER TIP:** Order matters here. Moving middleware to the wrong position can break logins or block requests.

```python
AUTH_USER_MODEL = 'core.User'
```

> **WHAT IT DOES:** Tells Django to use a custom user model defined in the `core` app.
> **WHY IT IS HERE:** NoteNest needs extra fields like `student_id`, `role`, and security questions.
> **BEGINNER TIP:** This must be set before you run your first migration — you cannot change it later without resetting the database.

```python
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://notenest-1-auxz.onrender.com']
```

> **WHAT IT DOES:** Allows the browser frontend to call the backend API from a different URL, and trusts the Render domain for POST requests.
> **WHY IT IS HERE:** The frontend is hosted separately from the backend, so CORS and CSRF must be configured.

---

### `urls.py` (project-level)

**What is this file?**
The receptionist of the project. It looks at the URL of a request and sends it to the right place.

```python
def api_root(request):
    return JsonResponse({
        "status": "ok",
        "project": "NoteNest API",
        "endpoints": { ... }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/admin/', include('core.urls')),
]
```

> **WHAT IT DOES:** Sends `/` to a health-check JSON response, `/admin/` to Django's admin panel, and `/api/admin/...` to the core app's API routes.
> **WHY IT IS HERE:** Without this, every request would return 404.
> **BEGINNER TIP:** `include('core.urls')` means the `core` app defines its own routes in a separate file.

---

### `wsgi.py`

**What is this file?**
The entry point for production servers like Gunicorn.

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.notenest_project.settings')
application = get_wsgi_application()
```

> **WHAT IT DOES:** Sets the settings module and creates a WSGI application object.
> **WHY IT IS HERE:** Gunicorn uses the `application` object to forward web requests into Django.
> **BEGINNER TIP:** If the path or settings name is wrong here, the production server cannot start.

---

### `core/models.py`

**What is this file?**
Defines the database tables and their fields using Python classes. Django turns these into real database tables.

#### `User` model

```python
class User(AbstractUser):
    student_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, choices=[('admin','Admin'),('student','Student')], default='student')
    security_question = models.CharField(max_length=255, blank=True)
    security_answer = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
```

> **WHAT IT DOES:** Extends Django's built-in user with student-specific fields and a role system.
> **WHY IT IS HERE:** The app needs student IDs, roles, and security questions for password recovery.
> **BEGINNER TIP:** `AbstractUser` gives you all normal user features (password hashing, login) for free — you just add your own fields.

#### `Semester` and `Course` models

```python
class Semester(models.Model):
    number = models.IntegerField(unique=True)
    label = models.CharField(max_length=50)

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    credit_hours = models.FloatField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
```

> **WHAT IT DOES:** Stores semester and course data, with courses linked to semesters.
> **WHY IT IS HERE:** The frontend shows courses organized by semester.
> **BEGINNER TIP:** `ForeignKey` is how Django links tables — like a bridge between two tables. `on_delete=CASCADE` means if the semester is deleted, all its courses are deleted too.

#### `QuestionPaper` model

```python
class QuestionPaper(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.CharField(max_length=10)
    drive_link = models.URLField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

> **WHAT IT DOES:** Stores a Google Drive link to each question paper, along with metadata.
> **WHY IT IS HERE:** Question papers are the main content students want.
> **BEGINNER TIP:** `auto_now_add=True` means Django automatically records the time when the paper was uploaded — you never have to set it manually.

#### `Bookmark` and `ActivityLog` models

```python
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
```

> **WHAT IT DOES:** Saves bookmarks and records user actions like logging in or viewing a paper.
> **WHY IT IS HERE:** Students need personal bookmarks and history tracking.

> **What you just learned:** `models.py` describes the data structure in Python. Django reads it and creates matching database tables automatically.

---

### `core/serializers.py`

**What is this file?**
Converts Django model objects into JSON (and back). The frontend speaks JSON. Django models are Python objects. Serializers are the translators between them.

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'student_id', 'email', 'role', 'date_joined']
```

> **WHAT IT DOES:** Defines exactly which user fields are included in API responses.
> **WHY IT IS HERE:** You never want to expose sensitive fields like passwords in the API response.
> **BEGINNER TIP:** Think of a serializer as a filter — it decides what goes in and what stays out.

```python
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['student_id'],
            password=validated_data['password'],
            ...
        )
        return user
```

> **WHAT IT DOES:** Validates signup input and creates a new user with a hashed password.
> **WHY IT IS HERE:** You never save raw passwords to the database — Django hashes them automatically via `create_user`.
> **BEGINNER TIP:** `write_only=True` means the password is accepted in input but never returned in responses.

---

### `core/views.py`

**What is this file?**
The brains of the API. Views receive requests, talk to the database, and return responses.

#### `LoginView`

```python
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        # ... find user by email or student_id ...
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': { ... }})
```

> **WHAT IT DOES:** Accepts a login request, checks credentials, and returns an authentication token.
> **WHY IT IS HERE:** This is how students prove who they are to the API.
> **BEGINNER TIP:** `permission_classes = [AllowAny]` means this endpoint is public — anyone can call it, because you obviously need to log in without being logged in.

#### `SemesterListView`

```python
class SemesterListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Semester.objects.prefetch_related('courses').all()
    serializer_class = SemesterSerializer
```

> **WHAT IT DOES:** Returns all semesters with their nested courses in one JSON response.
> **BEGINNER TIP:** `prefetch_related('courses')` is a performance optimization — it fetches all related course data in one database query instead of one query per semester.

---

### `core/urls.py`

**What is this file?**
Maps API paths to view classes for the `core` app.

```python
urlpatterns = [
    path('auth/login/',               views.LoginView.as_view()),
    path('auth/signup/',              views.SignupView.as_view()),
    path('auth/me/',                  views.UserMeView.as_view()),
    path('auth/forgot-password/',     views.ForgotPasswordView.as_view()),
    path('auth/reset-password/',      views.ResetPasswordView.as_view()),
    path('semesters/',                views.SemesterListView.as_view()),
    path('faculty/',                  views.AdminFacultyListCreateView.as_view()),
    path('faculty/<int:pk>/',         views.AdminFacultyDeleteView.as_view()),
    path('questions/',                views.AdminQuestionListCreateView.as_view()),
    path('questions/<int:pk>/',       views.AdminQuestionDeleteView.as_view()),
    path('overview/',                 views.AdminOverviewView.as_view()),
    path('users/',                    views.AdminUserListView.as_view()),
    path('student/bookmarks/',        views.BookmarkListCreateView.as_view()),
    path('student/bookmarks/<int:question_paper_id>/', views.BookmarkDeleteView.as_view()),
    path('student/history/',          views.ActivityLogListView.as_view()),
    path('student/log-view/',         views.LogQuestionView.as_view()),
]
```

> **WHAT IT DOES:** Every URL in the API is listed here with its view.
> **WHY IT IS HERE:** Without these routes, every API request would return 404.
> **BEGINNER TIP:** `<int:pk>` is a URL parameter — it captures a number from the URL (e.g. `/faculty/3/` gives `pk=3`) so the view knows which record to act on.

---

### `core/permissions.py`

**What is this file?**
Custom access rules that decide who is allowed to call each endpoint.

```python
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsAuthenticatedAndAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True   # Anyone can read
        return request.user.is_authenticated and request.user.role == 'admin'
```

> **WHAT IT DOES:** `IsAdmin` blocks non-admins. `IsAuthenticatedAndAdminOrReadOnly` lets anyone view data but only admins create or delete it.
> **WHY IT IS HERE:** Students should be able to browse question papers but not upload or delete them.

---

### `core/admin.py`

**What is this file?**
Registers models with Django's built-in admin panel so they can be managed through a web interface.

```python
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credit_hours', 'semester']
    list_filter = ['semester']
    search_fields = ['code', 'name']
```

> **WHAT IT DOES:** Makes courses searchable and filterable in the admin panel at `/admin/`.
> **BEGINNER TIP:** Visit `/admin/` with the admin credentials to manage all data through a visual interface — no code needed.

---

### `core/migrations/`

**What is this folder?**
The versioned history of every database change.

**How migrations work:**

```
You edit models.py
       ↓
python manage.py makemigrations   ← creates a new migration file
       ↓
python manage.py migrate          ← applies the change to the actual database
```

- `0001_initial.py` — creates the first set of database tables (users, semesters, courses, question papers, faculty)
- `0002_activitylog_bookmark.py` — adds the `Bookmark` and `ActivityLog` tables

> **BEGINNER TIP:** This trips up a lot of beginners — take it slowly. If the code and database schema don't match, the app breaks. Always run `migrate` after pulling new changes.

---

### `core/management/commands/seed_data.py`

**What is this file?**
A custom Django command that fills the database with sample data for testing and development.

```python
class Command(BaseCommand):
    help = 'Seed the database with semesters, courses, faculty, and admin user'
```

Run it with:

```bash
python manage.py seed_data
```

> **WHAT IT DOES:** Creates 8 semesters, dozens of courses, sample faculty, and default student and admin accounts.
> **BEGINNER TIP:** Default credentials after seeding — Student: `student@notenest.com` / `123456`. Admin: `admin@notenest.com` / `admin123`.

---

### `build.sh`

**What is this file?**
A shell script that runs during deployment to prepare the app.

```bash
#!/bin/bash
set -o errexit
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput
echo "Build complete!"
```

Step by step:
1. `set -o errexit` — stop immediately if any command fails
2. Delete stale Python cache files
3. Apply database migrations
4. Collect static files (CSS, JS) into `staticfiles/`

> **BEGINNER TIP:** `--noinput` means the command will not pause and ask questions during deployment.

---

### `requirements.txt`

**What is this file?**
Lists every Python package the project needs.

```
django>=5.0
djangorestframework>=3.14
django-cors-headers>=4.0
python-dotenv>=1.0
gunicorn>=20.1.0
whitenoise>=6.0
dj-database-url>=1.0
psycopg2-binary>=2.9
```

| Package | Purpose |
|---------|---------|
| `django` | The web framework |
| `djangorestframework` | Adds REST API tools to Django |
| `django-cors-headers` | Handles cross-origin browser requests |
| `python-dotenv` | Loads `.env` files for local development |
| `gunicorn` | Production-grade web server |
| `whitenoise` | Serves static files (CSS/JS) from Django |
| `dj-database-url` | Parses `DATABASE_URL` environment variable |
| `psycopg2-binary` | PostgreSQL database driver |

---

### `render.yaml`

**What is this file?**
Tells Render how to build, run, and configure the app automatically.

```yaml
services:
  - type: web
    name: notenest
    env: python
    buildCommand: pip install -r requirements.txt && bash build.sh
    startCommand: gunicorn backend.notenest_project.wsgi --bind 0.0.0.0:$PORT
    envVars:
      - key: SECRET_KEY
        value: ""
      - key: DEBUG
        value: "False"
```

> **WHAT IT DOES:** Defines the build command (install packages + run build.sh), the start command (launch Gunicorn), and required environment variables.
> **BEGINNER TIP:** Never hardcode `SECRET_KEY` in this file — set it in Render's Environment dashboard instead.

> **What you just learned:** Each backend file plays a specific role. Configuration, data models, API logic, routing, permissions, and deployment scripts all work together to form the Django API.

---

## PART 4 — Frontend files explained

---

### `frontend/index.html`

**What is an HTML file?**
The skeleton of a web page. It defines structure, sections, buttons, and input fields, and links to the CSS and JavaScript files.

**Structure overview:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="style.css">   <!-- loads styling -->
</head>
<body>
    <!-- all page content here -->
    <script src="script.js"></script>           <!-- loads logic, always last -->
</body>
</html>
```

**Major sections in the page:**

| Section | Purpose |
|---------|---------|
| Navbar | Top navigation links and login/signup buttons |
| Home | Hero banner and subject cards |
| Subjects | Semester-based course lists |
| Questions | Question paper browser with term filter |
| Faculty | Faculty directory cards |
| Admin dashboard | Upload papers, manage faculty, view users |
| Student dashboard | Profile, bookmarks, activity history |
| Auth modal | Login, signup, and password reset forms |
| Footer | Site links and team credits |

> **BEGINNER TIP:** Elements with `id="..."` are targeted by JavaScript to show, hide, or update content dynamically.

---

### `frontend/style.css`

**What is CSS?**
The styling language for web pages. It controls colors, spacing, fonts, layout, and visual design — it turns raw HTML into a designed page.

**CSS variables:**

```css
:root {
    --primary: #6366f1;
    --secondary: #10b981;
    --dark: #0f172a;
    --light: #f8fafc;
    --radius: 12px;
}
```

> **WHAT IT DOES:** Defines reusable colors and values for the whole stylesheet.
> **WHY IT IS HERE:** Variables make it easy to change the theme in one place and have it update everywhere.
> **BEGINNER TIP:** Use `var(--primary)` anywhere in the stylesheet to apply the main purple color.

**Major sections:**

| Section | What it styles |
|---------|---------------|
| Global styles | Font, spacing resets, box-sizing |
| Navbar | Sticky top bar, link hover effects |
| Buttons | Primary and outline styles, hover animations |
| Hero | Big title, background, call-to-action |
| Cards and grids | Subject cards and feature cards |
| Modals | Overlay, sliding animation, show/hide |
| Footer | Dark background, link colors |

---

### `frontend/script.js`

**What is JavaScript's role?**
JavaScript makes the page interactive. It handles clicks, fetches data from the backend, updates the screen, and manages login state — all without reloading the page.

**Base URL:**

```js
const API_BASE = 'https://notenest-1-auxz.onrender.com/api/admin/';
```

> **BEGINNER TIP:** If the backend URL ever changes, only this one line needs to be updated.

**The `fetchAPI` function — the core of all communication:**

```js
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.token) {
        headers['Authorization'] = `Token ${currentUser.token}`;
    }
    const response = await fetch(`${API_BASE}${endpoint}`, { method, headers, body: body ? JSON.stringify(body) : null });
    return response.json();
}
```

> **WHAT IT DOES:** Builds a request with the correct headers (including the auth token), sends it to the backend, and returns the JSON response.
> **BEGINNER TIP:** `async/await` is JavaScript's way of waiting for a network request to finish before continuing. Without it, the code would try to use the response before it arrives.

**Login flow:**

```js
async function login(identifier, password) {
    const res = await fetchAPI('auth/login/', 'POST', { identifier, password });
    if (res && res.token) {
        setCurrentUser({ token: res.token, ...res.user });
        await loadInitialData();
        return { success: true };
    }
}
```

> **WHAT IT DOES:** Sends credentials to the backend and stores the returned token in `localStorage`.
> **BEGINNER TIP:** `localStorage` keeps data in the browser even after a page refresh, so the user stays logged in.

**Token storage:**

```js
function setCurrentUser(user) {
    localStorage.setItem('notenest_user', JSON.stringify(user));
}
function getCurrentUser() {
    return JSON.parse(localStorage.getItem('notenest_user'));
}
```

> **WHAT IT DOES:** Saves and retrieves the logged-in user (including token) from browser storage.
> **WHY IT IS HERE:** The token is sent with every protected API request so the backend knows who is asking.

**Page rendering functions:**

| Function | What it renders |
|----------|----------------|
| `renderSubjectsPage()` | Semester and course cards |
| `renderQuestionsPage()` | Question paper list with filters |
| `renderFacultyPage()` | Faculty directory cards |
| `renderAdminOverview()` | Admin stats and management tools |
| `renderStudentProfile()` | Bookmark list and activity history |

**App initialization:**

```js
async function init() {
    updateUI();
    await loadInitialData();
    if (getCurrentUser()) { showDashboard(); }
    else { showHome(); }
}
init();
```

> **WHAT IT DOES:** Runs as soon as the page loads — sets up the UI, loads data, and decides whether to show the home page or the dashboard.
> **BEGINNER TIP:** `init()` is the starting point of the whole frontend application. Everything begins here.

> **What you just learned:** `script.js` is the dynamic engine of the site. It fetches API data, updates the screen, manages login state, and controls page navigation.

---

## PART 5 — Django concepts for beginners

### 1. What is Django?

Django is a Python framework for building web applications. Instead of writing everything from scratch, you get ready-made tools for:

- Routing URLs to code
- Talking to databases with Python (no SQL needed)
- Handling user login and security
- Returning HTTP responses

> **Analogy:** Django is like a furnished apartment. You still have to live there and decorate it, but the kitchen, bathroom, and electricity are already installed.

---

### 2. What is a model?

A model is a Python class that represents a database table. Each attribute is a column, and each instance is a row.

```python
class QuestionPaper(models.Model):
    term = models.CharField(max_length=10)
    drive_link = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

> **Analogy:** A model is like a form template. Every filled-in form is one row in the database.

---

### 3. What is a view?

A view is a function or class that handles an HTTP request and returns a response.

```python
class LoginView(APIView):
    def post(self, request):
        # check credentials
        return Response({'token': token.key})
```

> **Analogy:** A view is like a cashier at a shop — it receives your order (request), processes it, and hands back what you asked for (response).

---

### 4. What is a URL pattern?

A URL pattern maps a web address to a view.

```python
path('auth/login/', views.LoginView.as_view())
```

> **Analogy:** URL patterns are like a building directory. "Room 204 = login desk. Room 301 = question papers."

---

### 5. What is a serializer?

A serializer converts Django model objects into JSON for the frontend, and converts JSON from the frontend back into model objects.

```python
class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
```

> **Analogy:** A serializer is like a translator at a meeting between two people who speak different languages. Django speaks Python objects; the browser speaks JSON.

---

### 6. What is a migration?

A migration is a versioned database change generated from `models.py`.

```bash
# Workflow:
python manage.py makemigrations   # generate the migration file
python manage.py migrate          # apply it to the database
```

> **Analogy:** Migrations are like Git commits for your database schema. Each one records exactly what changed and can be applied in order on any machine.

---

### 7. What is an authentication token?

A token is a secret string the server gives you after login. You send it with every future request to prove you are logged in.

```
Login → server returns "abc123xyz"
Future request → header: "Authorization: Token abc123xyz"
```

> **Analogy:** A token is like a wristband at a concert. You show ID once at the gate, get the wristband, and then move freely without showing ID again.

---

### 8. What is CORS?

CORS (Cross-Origin Resource Sharing) is a browser security rule that blocks a web page from calling a different server unless that server explicitly allows it.

In NoteNest, `django-cors-headers` with `CORS_ALLOW_ALL_ORIGINS = True` allows the frontend to call the backend even though they are on different URLs.

> **Analogy:** CORS is like a bouncer who only lets in people on the guest list. `CORS_ALLOW_ALL_ORIGINS = True` is telling the bouncer "everyone is on the list."

---

### 9. What is Gunicorn?

Gunicorn is a production-ready Python web server. Django's built-in `runserver` is only for local development — it is not fast or stable enough for real users.

```bash
gunicorn backend.notenest_project.wsgi --bind 0.0.0.0:$PORT
```

> **Analogy:** Django's built-in server is like a student doing a practice run. Gunicorn is the professional hired for the real event.

---

### 10. What is WhiteNoise?

WhiteNoise serves static files (CSS, JS, images) directly from Django without needing a separate web server like Nginx.

It is activated by adding it to `MIDDLEWARE` and running `collectstatic` during deployment.

> **What you just learned:** These 10 concepts power every part of NoteNest. Understanding them means you can read and modify any Django project, not just this one.

---

## PART 6 — How data flows through the whole app

### Journey 1 — Student logs in

```
Step 1  Student types email/student ID + password and clicks Login

Step 2  script.js calls:
        POST https://notenest-1-auxz.onrender.com/api/admin/auth/login/
        Body: { "identifier": "student@notenest.com", "password": "123456" }

Step 3  Django receives it → notenest_project/urls.py matches:
        path('api/admin/', include('core.urls'))
        → core/urls.py matches:
        path('auth/login/', views.LoginView.as_view())

Step 4  LoginView.post() runs in views.py

Step 5  The view finds the user by email or student_id
        Calls user.check_password(password)

Step 6  Database returns the User object if credentials match

Step 7  Django responds with JSON:
        { "token": "abc123xyz", "user": { "studentId": "...", "role": "student" } }

Step 8  script.js stores the token in localStorage
        Calls loadInitialData() to refresh the page

Step 9  The student sees their dashboard
```

---

### Journey 2 — Student views question papers

```
Step 1  Student selects Semester 3 and term "Au-25"

Step 2  script.js calls:
        GET https://notenest-1-auxz.onrender.com/api/admin/questions/?semester=3&term=Au-25
        Header: Authorization: Token abc123xyz

Step 3  Django receives it → matches:
        path('questions/', views.AdminQuestionListCreateView.as_view())

Step 4  AdminQuestionListCreateView.get_queryset() runs

Step 5  The view filters QuestionPaper.objects.filter(semester=3, term='Au-25')

Step 6  Database returns matching rows

Step 7  QuestionPaperSerializer converts rows to JSON:
        [ { "id": 1, "term": "Au-25", "drive_link": "https://...", ... }, ... ]

Step 8  script.js receives the JSON and calls renderQuestionsPage()

Step 9  The student sees paper cards with View/Download buttons
```

> **What you just learned:** Every user action is a chain of: browser event → JavaScript fetch → Django URL match → view logic → database query → JSON response → screen update.

---

## PART 7 — Deployment explained

### 1. What is Render.com?

Render is a cloud hosting service. You connect your GitHub repo, and Render automatically builds and runs your app every time you push new code.

### 2. What does `build.sh` do step by step?

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `find . -name __pycache__ -exec rm -rf {}` | Clear stale Python bytecode cache |
| 2 | `python manage.py migrate --noinput` | Apply any new database migrations |
| 3 | `python manage.py collectstatic --noinput` | Gather all CSS/JS files into `staticfiles/` |

### 3. What does `render.yaml` configure?

- Service type (`web`)
- Python version
- Build command (install packages + run `build.sh`)
- Start command (launch Gunicorn)
- Environment variables (SECRET_KEY, DEBUG, DATABASE_URL)

### 4. What is an environment variable?

A setting stored outside the source code. Examples:

| Variable | Why not hardcoded |
|----------|-------------------|
| `SECRET_KEY` | If leaked, attackers can forge sessions |
| `DEBUG` | Must be `False` in production — different from development |
| `DATABASE_URL` | Production database address differs from local |

### 5. What is Gunicorn doing?

It listens on a network port and forwards each incoming HTTP request into Django's WSGI application. It handles multiple requests at the same time efficiently.

### 6. What is a static file?

Files that never change on the server — CSS, JavaScript, images. WhiteNoise compresses them and serves them directly, removing the need for a separate web server.

### 7. SQLite vs PostgreSQL

| | SQLite | PostgreSQL |
|--|--------|------------|
| Best for | Local development | Production |
| Storage | A single file (`db.sqlite3`) | A database server |
| Concurrent users | Poor | Excellent |
| How NoteNest uses it | Default locally | Activated via `DATABASE_URL` env var |

> **What you just learned:** Deployment is not just pushing code. It is a pipeline of installing packages, migrating the database, collecting static files, and starting a production server.

---

## PART 8 — Glossary

| Term | Plain English definition |
|------|--------------------------|
| **Django** | A Python framework for building web apps — provides routing, database tools, security, and more |
| **REST API** | A web interface that uses HTTP to let programs talk to your app, returning JSON data |
| **JSON** | A text format for data: `{ "name": "NoteNest", "version": "1.0" }` |
| **HTTP** | The protocol browsers and servers use to communicate |
| **GET** | An HTTP request to read data |
| **POST** | An HTTP request to create or send data |
| **URL** | The web address of a page or API endpoint |
| **View** | The function or class that handles a request and returns a response |
| **Model** | A Python class that defines a database table |
| **Migration** | A versioned file that updates the database schema to match models.py |
| **Serializer** | A translator between Django objects (Python) and JSON (browser) |
| **Token** | A login key sent with requests instead of repeating username/password |
| **CORS** | A browser security rule that controls which servers a web page can call |
| **Gunicorn** | A production-grade web server for Python apps |
| **WhiteNoise** | A tool that serves static files (CSS/JS) from Django without a separate web server |
| **Environment variable** | A configuration setting stored outside the code |
| **Static files** | CSS, JavaScript, and images that are served as-is without processing |
| **Database** | Where all app data is permanently stored |
| **ORM** | Object Relational Mapper — lets you use Python instead of SQL to query the database |
| **Endpoint** | A specific URL where the API listens and responds |
| **Request** | What the browser sends to the backend |
| **Response** | What the backend sends back |
| **Frontend** | The browser-facing part of the app (HTML, CSS, JS) |
| **Backend** | The server-side part that processes requests and manages data |
| **render.yaml** | A configuration file that tells Render how to build and run the app |
| **AbstractUser** | Django's built-in user class that you can extend with extra fields |
| **ForeignKey** | A database link from one table to another |
| **Middleware** | Code that runs on every request before it reaches a view |
| **WSGI** | The standard interface between Python web apps and production web servers |
| **localhost** | Your own computer, accessed as a server during development |

---

## Default credentials (after running `seed_data`)

| Account | Email | Student ID | Password |
|---------|-------|------------|---------|
| Student | `student@notenest.com` | `student` | `123456` |
| Admin | `admin@notenest.com` | `admin` | `admin123` |

---

## Useful commands

```bash
# Start local development server
python backend/manage.py runserver

# Create database migrations after changing models.py
python backend/manage.py makemigrations

# Apply migrations to the database
python backend/manage.py migrate

# Fill the database with sample data
python backend/manage.py seed_data

# Collect static files
python backend/manage.py collectstatic

# Open the Django interactive shell
python backend/manage.py shell

# Run tests
python backend/manage.py test
```

---

*NoteNest — CSE Question Bank | International Islamic University Chittagong*
*Team: Azra Sadia Bithi · Eyenun Ilham Mawla · Mustabira Muntaha Moomo*
