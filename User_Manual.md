# NoteNest User Manual

Welcome to NoteNest! This manual will guide you through the features of the platform, both from a student's perspective and an administrator's perspective.

## Table of Contents
1. [General Navigation](#general-navigation)
2. [Student Features](#student-features)
3. [Admin Panel Guide](#admin-panel-guide)
   - [Logging In](#logging-in)
   - [Overview](#overview)
   - [Managing Faculty](#managing-faculty)
   - [Uploading Questions](#uploading-questions)
   - [User Management](#user-management)

---

## General Navigation

NoteNest is a single-page application. You can navigate through the platform using the top navigation bar.

*   **Home:** Overview of the platform, statistics, and popular subjects.
*   **Subjects:** A complete breakdown of the CSE curriculum, organized by semester. You must be logged in to click on specific subjects.
*   **Faculty Info:** A searchable directory of all IIUC CSE faculty members. You must be logged in to view this directory.
*   **Questions:** Browse previous year question papers by Semester -> Year/Term -> Subject.
*   **Login:** Access your Student or Admin dashboard.

---

## Student Features

### Accessing the Platform & Account Creation
As a student, you must log in to access course details, view question papers, search faculty, and bookmark files.

*   **Sign Up**: Click "Sign Up" in the navigation bar or auth modal. Fill in your Student ID, Email, Password, select a **Security Question**, and provide a **Security Answer**. This answer is crucial for password recovery.
*   **Sign In**: Click "Login", enter your email or Student ID, and your password.
*   **Password Recovery**: If you forget your password, click the "Forgot Password?" link on the login form. Enter your email or Student ID to retrieve your security question, answer it correctly, and set a new password.

*For quick testing, you can use the default seeded student account:*
*   **Email:** `student` (or `student@notenest.com`)
*   **Password:** `123456`

### Finding & Viewing Question Papers
1. Click on **Questions** in the top navigation.
2. Select your target **Semester** (e.g., "1st Semester").
3. Select the **Term/Year** you are looking for (e.g., "Au-24").
4. A list of subjects will appear with status badges:
   *   **Available**: Question paper has been uploaded. Click it to view details (course code, name, description), download it via the Google Drive link, or bookmark it.
   *   **Coming Soon**: No paper has been uploaded yet. Click to view the "Coming Soon" notification.

### Bookmarks & Activity History
Your student dashboard (accessed by clicking "Student Dashboard" in the navigation bar) includes:
*   **Profile**: View your student credentials and see if your security question is configured.
*   **Bookmarks**: View all question papers you have bookmarked. Click the external link to view/download the paper directly, or click the trash can icon to remove it.
*   **History**: Check your recent activity log (e.g., login times, registered actions, bookmarked or viewed papers).

### Faculty Directory
1. Click on **Faculty Info**.
2. Use the **Search Bar** to find a specific teacher by name or email.
3. Use the **Checkboxes** to filter teachers by their designation (e.g., only show "Professors").

---

## Admin Panel Guide

The Admin Panel is a secure area where authorized users can manage the platform's data. All data managed here is synced directly with the Django backend database.

### Logging In
To access the Admin Panel, you must log in with admin credentials.
*   **Email:** `admin@notenest.com`
*   **Password:** `admin123`

Once logged in, click on "Admin Dashboard" in the navigation bar.

### Overview
The **Overview** tab is your command center. It provides real-time statistics pulled directly from the backend database:
*   Total registered users.
*   Total uploaded question papers.
*   Total faculty members.
*   A list of the 5 most recently uploaded question papers.

### Uploading Questions
The **Upload Questions** tab allows you to add new question papers to the database.
1. Select the **Semester**.
2. The **Subject** dropdown will automatically populate based on the chosen semester. Select the relevant subject.
3. Select the **Term** (e.g., "Au-24").
4. Provide a valid **Google Drive or PDF Link** where the question paper is hosted.
5. Click **Upload**.
6. The new question paper will immediately appear in the "Uploaded Questions" list below. You can delete incorrect entries using the red trash can icon.

### Managing Faculty
The **Manage Faculty** tab allows you to maintain the faculty directory.
1. **To Add:** Fill in the Name, Position (from the dropdown), and Email, then click "Add Faculty". This saves the new faculty member to the database, making them instantly searchable on the public "Faculty Info" page.
2. **To Remove:** Scroll down to the "All Faculty" table and click the red trash can icon next to the person you wish to remove.

### User Management
The **Users** tab displays a list of all registered accounts (students and admins) pulled from the database. 
*   You can see their Student ID, Email, and current Role.
*   *(Role promotion functionality is visible in the UI but relies on further backend configuration to permanently elevate student privileges).*
