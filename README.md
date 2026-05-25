111f-# NoteNest - CSE Question Bank

NoteNest is a comprehensive academic platform designed specifically for the students of the Computer Science and Engineering (CSE) Department at the International Islamic University Chittagong (IIUC). It serves as a centralized hub for previous year question papers, faculty information, and semester-wise course details.

![NoteNest Preview](frontend/style.css) *Note: Add a screenshot of the project here*

## Features

*   **Extensive Question Bank:** Access 1000+ previous year question papers filtered by semester and subject.
*   **Faculty Directory:** Complete list of faculty members with their designations and contact emails.
*   **Course Curriculum:** Detailed breakdown of courses, credit hours, and prerequisites for all 8 semesters.
*   **Admin Dashboard:** A secure panel for administrators to manage users, faculty data, and upload new question papers.
*   **Responsive Design:** Fully mobile-friendly interface built with modern CSS variables and flexbox.

## Tech Stack

*   **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (Vanilla, Fetch API)
*   **Backend:** Django, Django REST Framework (DRF)
*   **Database:** SQLite (Development)
*   **Icons:** FontAwesome

## Project Structure

The project is decoupled into two separate directories:

*   `frontend/`: Contains the client-side code (`index.html`, `style.css`, `script.js`).
*   `backend/`: Contains the Django application and SQLite database.

---

## How to Run the Project Locally

### 1. Backend Setup (Django)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install django djangorestframework django-cors-headers
   ```
4. Run database migrations:
   ```bash
   python manage.py migrate
   ```
5. Seed the database with initial data (Semesters, Courses, Faculty, Admin User):
   ```bash
   python manage.py seed_data
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
    *The backend API will now be running at `http://127.0.0.1:8000/api/admin/`*

### 2. Frontend Setup

1. Open a new terminal.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Since the frontend makes API calls via JavaScript `fetch()`, serve the frontend using a local web server (using port `8080` since Django occupies port `8000`):
   ```bash
   # Using Python's built-in HTTP server
   python -m http.server 8080
   ```
4. Open your browser and navigate to `http://localhost:8080`.

---

## Default User Credentials

If you ran the `seed_data` command, the following default accounts are seeded:

*   **Student Account**:
    *   **Email / Student ID:** `student@notenest.com` (or `student`)
    *   **Password:** `123456`
*   **Admin Account**:
    *   **Email / Username:** `admin@notenest.com` (or `admin`)
    *   **Password:** `admin123`

You can use these credentials to log into the application frontend or the Django Admin panel (`http://127.0.0.1:8000/admin/`).

## API Endpoints

The following RESTful endpoints are exposed by the backend:

### Authentication & Profiles
*   `POST /api/admin/auth/signup/` - Register a new student account.
*   `POST /api/admin/auth/login/` - Authenticate credentials and receive an API token.
*   `GET /api/admin/auth/me/` - Retrieve logged-in user profile details.
*   `GET /api/admin/auth/forgot-password/` - Retrieve security question for password recovery.
*   `POST /api/admin/auth/reset-password/` - Reset password via security answer.

### Shared Data Endpoints
*   `GET /api/admin/semesters/` - List of all semesters with nested courses (public).
*   `GET /api/admin/faculty/` - Searchable directory of faculty members (student/admin auth required).
*   `GET /api/admin/questions/` - List question papers. Can filter by query parameters, e.g. `?semester=1&term=Au-24`.

### Student Actions
*   `GET /api/admin/student/bookmarks/` - List student's bookmarked question papers.
*   `POST /api/admin/student/bookmarks/` - Bookmark a question paper.
*   `DELETE /api/admin/student/bookmarks/<question_paper_id>/` - Remove a bookmarked paper.
*   `GET /api/admin/student/history/` - View recent activity history logs.
*   `POST /api/admin/student/log-view/` - Log paper downloads/view actions.

### Administrative Control
*   `GET /api/admin/overview/` - Fetch overview statistics (total users, papers, faculty, semesters).
*   `GET /api/admin/users/` - View all registered accounts.
*   `POST /api/admin/faculty/` - Add a new faculty member.
*   `DELETE /api/admin/faculty/<id>/` - Delete a faculty member.
*   `POST /api/admin/questions/` - Upload a new question paper.
*   `DELETE /api/admin/questions/<id>/` - Delete an uploaded question paper.

## Team NoteNest

*   **Azra Sadia Bithi** (C251246)
*   **Eyenun Ilham Mawla** (C251262)
*   **Mustabira Muntaha Moomo** (C251239)

Developed for the CSE Department, IIUC.
