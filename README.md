# NoteNest — CSE Question Bank

NoteNest is a comprehensive academic platform designed specifically for the students of the Computer Science and Engineering (CSE) Department at the International Islamic University Chittagong (IIUC). It serves as a centralized hub for previous year question papers, faculty information, and semester-wise course details.

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | [https://notenest-v0zw.onrender.com](https://notenest-v0zw.onrender.com) |
| **Backend API** | [https://notenest-1-auxz.onrender.com](https://notenest-1-auxz.onrender.com) |
| **Django Admin** | [https://notenest-1-auxz.onrender.com/admin/](https://notenest-1-auxz.onrender.com/admin/) |

> **Note:** Both services are hosted on Render's free tier. If the app is inactive, the first request may take 30–60 seconds to wake up.

---

## Features

- **Extensive Question Bank:** Access 1000+ previous year question papers filtered by semester and subject.
- **Faculty Directory:** Complete list of faculty members with their designations and contact emails.
- **Course Curriculum:** Detailed breakdown of courses, credit hours, and prerequisites for all 8 semesters.
- **Admin Dashboard:** A secure panel for administrators to manage users, faculty data, and upload new question papers.
- **Responsive Design:** Fully mobile-friendly interface built with modern CSS variables and flexbox.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript (Vanilla, Fetch API) |
| **Backend** | Django 6, Django REST Framework |
| **Database** | SQLite (development), PostgreSQL (production) |
| **Server** | Gunicorn + WhiteNoise |
| **Hosting** | Render.com |
| **Icons** | FontAwesome |

---

## Project Structure

The project is decoupled into two separate directories:

```
NoteNest/
├── frontend/       # Client-side code (index.html, style.css, script.js)
└── backend/        # Django application and database
```

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
   pip install -r requirements.txt
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

   The backend API will now be running at `http://127.0.0.1:8000/api/admin/`

---

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Serve the frontend using Python's built-in HTTP server (port `8080` since Django occupies `8000`):
   ```bash
   python -m http.server 8080
   ```

3. Open your browser and navigate to `http://localhost:8080`.

---

## Default User Credentials

After running `python manage.py seed_data`, the following accounts are available:

| Role | Email | Student ID | Password |
|------|-------|------------|---------|
| **Student** | `student@notenest.com` | `student` | `123456` |
| **Admin** | `admin@notenest.com` | `admin` | `admin123` |

You can also use these credentials to log into the Django Admin panel at:
- Local: `http://127.0.0.1:8000/admin/`
- Live: `https://notenest-1-auxz.onrender.com/admin/`

---

## API Endpoints

Base URL: `https://notenest-1-auxz.onrender.com/api/admin/`

### Authentication & Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup/` | Register a new student account |
| `POST` | `/auth/login/` | Authenticate and receive an API token |
| `GET` | `/auth/me/` | Retrieve logged-in user profile |
| `GET` | `/auth/forgot-password/` | Retrieve security question for password recovery |
| `POST` | `/auth/reset-password/` | Reset password via security answer |

### Shared Data

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| `GET` | `/semesters/` | All semesters with nested courses | No |
| `GET` | `/faculty/` | Searchable faculty directory | Yes |
| `GET` | `/questions/` | List question papers (filter: `?semester=1&term=Au-24`) | No |

### Student Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/student/bookmarks/` | List bookmarked question papers |
| `POST` | `/student/bookmarks/` | Bookmark a question paper |
| `DELETE` | `/student/bookmarks/<id>/` | Remove a bookmark |
| `GET` | `/student/history/` | View activity history |
| `POST` | `/student/log-view/` | Log a paper view or download |

### Admin Controls

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/overview/` | Stats: total users, papers, faculty, semesters |
| `GET` | `/users/` | List all registered accounts |
| `POST` | `/faculty/` | Add a new faculty member |
| `DELETE` | `/faculty/<id>/` | Delete a faculty member |
| `POST` | `/questions/` | Upload a new question paper |
| `DELETE` | `/questions/<id>/` | Delete a question paper |

---

## Deployment

This project is deployed on [Render.com](https://render.com).

- **Backend** is a Python web service running Gunicorn.
- **Frontend** is a static site served directly from the `frontend/` folder.
- Deployment is automatic on every push to the `main` branch.

See [`render.yaml`](./render.yaml) and [`build.sh`](./build.sh) for the full deployment configuration.

---

## Team NoteNest

| Name | Student ID |
|------|------------|
| Azra Sadia Bithi | C251246 |
| Eyenun Ilham Mawla | C251262 |
| Mustabira Muntaha Moomo | C251239 |

Developed for the CSE Department, IIUC.
