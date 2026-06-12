// ============================================
// CONSTANTS & STATE
// ============================================
const API_BASE = 'https://notenest-1-auxz.onrender.com/api/admin/';
let semesterCourses = {};
let facultyData = [];
let adminOverview = {};
let allUsers = [];
let allQuestions = [];

const STORAGE_KEYS = { CURRENT_USER: 'notenest_current_user' };

// ============================================
// API HELPERS
// ============================================
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.token) {
        headers['Authorization'] = `Token ${currentUser.token}`;
    }

    const options = {
        method,
        headers,
        credentials: 'omit'
    };
    if (body) options.body = JSON.stringify(body);
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (method === 'DELETE' && response.status === 204) {
            return true;
        }
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            let msg = errData.error || errData.detail;
            if (!msg) {
                const errors = [];
                for (const key in errData) {
                    if (Array.isArray(errData[key])) {
                        errors.push(`${key.replace('_', ' ')}: ${errData[key].join(', ')}`);
                    } else if (typeof errData[key] === 'string') {
                        errors.push(`${key.replace('_', ' ')}: ${errData[key]}`);
                    }
                }
                if (errors.length > 0) {
                    msg = errors.join(' | ');
                }
            }
            throw new Error(msg || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (e) {
        console.error(`API Error on ${endpoint}:`, e);
        showToast(e.message || 'API request failed', 'error');
        return null;
    }
}

async function loadInitialData() {
    // Fetch Semesters & Courses (Publicly accessible now)
    const semesters = await fetchAPI('semesters/');
    if (semesters) {
        semesterCourses = {};
        semesters.forEach(sem => {
            semesterCourses[sem.number] = sem.courses.map(c => ({
                code: c.code,
                name: c.name,
                credit: c.credit_hours,
                prereq: c.prerequisite || '-'
            }));
        });
    }

    // Fetch Faculty (Accessible if logged in)
    if (getCurrentUser()) {
        const faculty = await fetchAPI('faculty/');
        if (faculty) facultyData = faculty;
    }
}

// ============================================
// AUTH SYSTEM
// ============================================
function getCurrentUser() { return JSON.parse(localStorage.getItem(STORAGE_KEYS.CURRENT_USER)); }
function setCurrentUser(user) { localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify(user)); }
function clearCurrentUser() { localStorage.removeItem(STORAGE_KEYS.CURRENT_USER); }

async function login(identifier, password) {
    const res = await fetchAPI('auth/login/', 'POST', { identifier, password });
    if (res && res.token) {
        const userData = {
            id: res.user.id,
            studentId: res.user.studentId,
            email: res.user.email,
            role: res.user.role,
            token: res.token
        };
        setCurrentUser(userData);
        // Reload data since we are now logged in
        await loadInitialData();
        return { success: true, message: 'Login successful!' };
    }
    return { success: false, message: 'Invalid credentials!' };
}

async function signup(studentId, email, password, securityQuestion, securityAnswer) {
    const body = {
        student_id: studentId,
        email: email,
        password: password,
        security_question: securityQuestion,
        security_answer: securityAnswer
    };
    const res = await fetchAPI('auth/signup/', 'POST', body);
    if (res) {
        return { success: true, message: 'Account created successfully! Please login.' };
    }
    return { success: false, message: 'Signup failed. Please try again.' };
}

function logout() { 
    clearCurrentUser(); 
    facultyData = [];
    updateUI(); 
    showToast('Logged out successfully', 'info'); 
    showHome(); 
}

function updateUI() {
    const user = getCurrentUser();
    const loginBtn = document.getElementById('loginBtn'), signupBtn = document.getElementById('signupBtn'), userProfile = document.getElementById('userProfile'), userName = document.getElementById('userName');
    const homeLink = document.getElementById('homeNavLink'), dashLink = document.getElementById('dashboardNavLink'), dashText = document.getElementById('dashboardNavText');
    const navAuthM = document.getElementById('navAuthMobile'), logoutNavM = document.getElementById('logoutNavLinkMobile');
    
    if (user) {
        if (loginBtn) loginBtn.style.display = 'none'; if (signupBtn) signupBtn.style.display = 'none';
        if (navAuthM) navAuthM.classList.remove('active');
        if (logoutNavM) logoutNavM.style.display = 'block';
        if (userProfile) { userProfile.style.display = 'flex'; if (userName) userName.textContent = user.studentId; }
        if (homeLink) homeLink.style.display = 'none';
        if (dashLink) { dashLink.style.display = 'inline'; if (dashText) dashText.textContent = user.role === 'admin' ? 'Admin Dashboard' : 'Student Dashboard'; }
    } else {
        if (loginBtn) loginBtn.style.display = ''; if (signupBtn) signupBtn.style.display = '';
        if (navAuthM) navAuthM.classList.add('active');
        if (logoutNavM) logoutNavM.style.display = 'none';
        if (userProfile) userProfile.style.display = 'none';
        if (homeLink) homeLink.style.display = 'inline';
        if (dashLink) dashLink.style.display = 'none';
    }
}

function toggleMobileMenu() { const nav = document.getElementById('navLinks'); const btn = document.getElementById('hamburgerBtn'); nav.classList.toggle('nav-open'); btn.classList.toggle('active'); }
function navClick(fn) { const nav = document.getElementById('navLinks'); const btn = document.getElementById('hamburgerBtn'); nav.classList.remove('nav-open'); btn.classList.remove('active'); fn(); }

// ============================================
// RENDER FUNCTIONS
// ============================================

function renderSubjectsPage() {
    const container = document.getElementById('subjectsContent');
    const currentUser = getCurrentUser();
    let html = '';
    
    if (Object.keys(semesterCourses).length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Loading courses from server...</p></div>';
        return;
    }

    for (let sem = 1; sem <= 8; sem++) {
        const courses = semesterCourses[sem] || [];
        const ordinal = sem === 1 ? "st" : sem === 2 ? "nd" : sem === 3 ? "rd" : "th";
        html += `<div class="semester-card"><div class="semester-header">${sem}${ordinal} Semester</div><table class="subjects-table"><thead><tr><th>SL</th><th>Course Code</th><th>Course Name</th><th>Credit Hours</th><th>Prerequisite</th></tr></thead><tbody>`;
        courses.forEach((course, idx) => {
            const displayCode = currentUser ? `<span class="subject-clickable" onclick="viewSubject('${course.code}', '${course.name.replace(/'/g, "\\'")}', ${sem})">${course.code}</span>` : course.code;
            html += `<tr><td>${idx + 1}</td><td>${displayCode}</td><td>${course.name}</td><td>${course.credit}</td><td>${course.prereq}</td></tr>`;
        });
        html += `</tbody></table></div>`;
    }
    if (!currentUser) html = `<div class="login-required-msg"><i class="fas fa-lock"></i><h3>Login Required</h3><p>Please login to access course details.</p><button class="btn btn-primary" onclick="openModal(); showLoginForm();">Login Now</button></div>` + html;
    container.innerHTML = html;
}

function viewSubject(code, name, sem) {
    if (!getCurrentUser()) { alert('Please login first!'); openModal(); return; }
    // Navigate to questions and select this course context automatically
    showQuestions();
    setTimeout(() => {
        selectSemester(sem);
    }, 100);
}

// QUESTIONS PAGE
let selectedSemester = null;
let selectedYear = '25';
let selectedSession = 'Autumn';
let selectedTerm = 'Mid';

function renderQuestionsPage() {
    const container = document.getElementById('questionsContent');
    let semesterBtns = '';
    for (let sem = 1; sem <= 8; sem++) {
        const ordinal = sem === 1 ? "st" : sem === 2 ? "nd" : sem === 3 ? "rd" : "th";
        semesterBtns += `<button class="semester-btn" onclick="selectSemester(${sem})">${sem}${ordinal} Semester</button>`;
    }
    container.innerHTML = `
        <div class="semester-buttons-grid" id="semesterButtonsGrid">
            ${semesterBtns}
        </div>
        <div id="subButtonsArea" style="display: none;"></div>
        <div id="subjectsDisplayArea" style="display: none;"></div>
    `;
    selectedSemester = null;
}

function selectSemester(semester) {
    selectedSemester = semester;
    document.getElementById('subButtonsArea').style.display = 'block';
    renderFilters();
    document.getElementById('subjectsDisplayArea').style.display = 'none';
    document.getElementById('subjectsDisplayArea').innerHTML = '';
    document.getElementById('subButtonsArea').scrollIntoView({ behavior: 'smooth' });
    fetchAndDisplayQuestions();
}

function renderFilters() {
    let filtersHtml = `
        <div class="questions-filter-panel">
            <div class="filter-section">
                <span class="filter-label"><i class="fas fa-calendar-alt"></i> Year</span>
                <div class="filter-chips" id="yearChips">
                    ${['26', '25', '24', '23', '22'].map(y => `
                        <button class="chip ${selectedYear === y ? 'active' : ''}" onclick="setFilter('year', '${y}')">20${y}</button>
                    `).join('')}
                </div>
            </div>
            
            <div class="filter-section">
                <span class="filter-label"><i class="fas fa-snowflake"></i> Session</span>
                <div class="filter-chips" id="sessionChips">
                    ${['Autumn', 'Spring'].map(s => `
                        <button class="chip ${selectedSession === s ? 'active' : ''}" onclick="setFilter('session', '${s}')">${s}</button>
                    `).join('')}
                </div>
            </div>
            
            <div class="filter-section">
                <span class="filter-label"><i class="fas fa-file-signature"></i> Term</span>
                <div class="filter-chips" id="termChips">
                    ${['Mid', 'Final'].map(t => `
                        <button class="chip ${selectedTerm === t ? 'active' : ''}" onclick="setFilter('term', '${t}')">${t === 'Mid' ? 'Midterm' : 'Final'}</button>
                    `).join('')}
                </div>
            </div>
        </div>
        <div class="back-btn"><button class="btn" onclick="renderQuestionsPage()">← Back to Semesters</button></div>
    `;
    document.getElementById('subButtonsArea').innerHTML = filtersHtml;
}

function setFilter(type, value) {
    if (type === 'year') {
        selectedYear = value;
    } else if (type === 'session') {
        selectedSession = value;
    } else if (type === 'term') {
        selectedTerm = value;
    }
    renderFilters();
    fetchAndDisplayQuestions();
}

async function fetchAndDisplayQuestions() {
    const semester = selectedSemester;
    const courses = semesterCourses[semester] || [];
    const ordinal = semester === 1 ? "st" : semester === 2 ? "nd" : semester === 3 ? "rd" : "th";

    // Query backend for available question papers in this semester, year, session, and term
    const questions = await fetchAPI(`questions/?semester=${semester}&year=${selectedYear}&session=${selectedSession}&term=${selectedTerm}`) || [];
    const questionsMap = {};
    questions.forEach(q => {
        questionsMap[q.course_code] = q;
    });

    let subjectsHtml = `
        <div class="subjects-list-container">
            <div class="selected-info">📖 ${semester}${ordinal} Semester - ${selectedSession} 20${selectedYear} (${selectedTerm === 'Mid' ? 'Midterm' : 'Final'})</div>
            <div class="subjects-list">
    `;
    courses.forEach(course => {
        const qPaper = questionsMap[course.code];
        let statusBadge = `<span class="q-status-badge coming-soon"><i class="fas fa-clock"></i> Coming Soon</span>`;
        let clickAction = `showComingSoon('${course.code}', '${course.name.replace(/'/g, "\\'")}', ${semester}, '${selectedYear}', '${selectedSession}', '${selectedTerm}')`;
        
        if (qPaper) {
            statusBadge = `<span class="q-status-badge available"><i class="fas fa-check-circle"></i> Available</span>`;
            clickAction = `showQuestionDetails('${qPaper.id}')`;
        }

        subjectsHtml += `
            <div class="subject-item" onclick="${clickAction}">
                <span class="subject-code">${course.code}</span>
                <span class="subject-name">${course.name}</span>
                ${statusBadge}
            </div>
        `;
    });
    subjectsHtml += `
            </div>
            <div id="questionDetailsArea" style="display: none; margin-top: 1.5rem;"></div>
        </div>
    `;

    document.getElementById('subjectsDisplayArea').style.display = 'block';
    document.getElementById('subjectsDisplayArea').innerHTML = subjectsHtml;
}

async function showQuestionDetails(qPaperId) {
    if (!getCurrentUser()) {
        showToast('Please login first to view question papers!', 'error');
        openModal();
        return;
    }

    const detailsArea = document.getElementById('questionDetailsArea');
    detailsArea.style.display = 'block';
    detailsArea.innerHTML = '<div style="text-align:center;padding:1rem;"><i class="fas fa-spinner fa-spin"></i> Loading details...</div>';

    // Retrieve details & check if bookmarked
    const bookmarks = await fetchAPI('student/bookmarks/') || [];
    const isBookmarked = bookmarks.some(b => b.question_paper == qPaperId);

    // Get specific question from allQuestions if cached, or query
    let qPaper = allQuestions.find(q => q.id == qPaperId);
    if (!qPaper) {
        // Fetch specific details (or just filter list)
        const papers = await fetchAPI(`questions/`) || [];
        qPaper = papers.find(q => q.id == qPaperId);
    }

    if (!qPaper) {
        detailsArea.innerHTML = '<div class="coming-soon-message">Failed to load paper details.</div>';
        return;
    }

    let bookmarkBtn = '';
    if (isBookmarked) {
        bookmarkBtn = `<button class="btn btn-outline btn-danger" onclick="removeBookmarkFromQuestion(${qPaper.id})"><i class="fas fa-bookmark"></i> Remove Bookmark</button>`;
    } else {
        bookmarkBtn = `<button class="btn btn-outline" onclick="bookmarkQuestion(${qPaper.id})"><i class="far fa-bookmark"></i> Bookmark Paper</button>`;
    }

    detailsArea.innerHTML = `
        <div class="coming-soon-message" style="background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-md); max-width: 500px; margin: 1rem auto; text-align: center;">
            <i class="fas fa-file-pdf" style="font-size: 2.5rem; color: var(--danger); margin-bottom: 0.5rem;"></i>
            <h3>Question Paper Available</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;"><strong>${qPaper.course_code} - ${qPaper.course_name}</strong></p>
            <p style="color: var(--text-muted); margin-bottom: 1rem;">Semester ${qPaper.semester_number} - Term ${qPaper.term}</p>
            ${qPaper.description ? `<p style="font-style: italic; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">"${qPaper.description}"</p>` : ''}
            <div class="btn-group" style="display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap;">
                <a href="${qPaper.drive_link}" target="_blank" class="btn btn-primary" onclick="logQuestionView(${qPaper.id})"><i class="fas fa-external-link-alt"></i> View / Download</a>
                ${bookmarkBtn}
            </div>
        </div>
    `;
    detailsArea.scrollIntoView({ behavior: 'smooth' });
}

async function logQuestionView(id) {
    await fetchAPI('student/log-view/', 'POST', { question_paper: id });
}

async function bookmarkQuestion(id) {
    const res = await fetchAPI('student/bookmarks/', 'POST', { question_paper: id });
    if (res) {
        showToast('Question paper bookmarked!', 'success');
        showQuestionDetails(id);
    }
}

async function removeBookmarkFromQuestion(id) {
    const res = await fetchAPI(`student/bookmarks/${id}/`, 'DELETE');
    if (res) {
        showToast('Bookmark removed', 'info');
        showQuestionDetails(id);
    }
}

function showComingSoon(code, name, semester, year, session, term) {
    const ordinal = semester === 1 ? "st" : semester === 2 ? "nd" : semester === 3 ? "rd" : "th";
    const messageDiv = document.createElement('div');
    messageDiv.className = 'coming-soon-message';
    messageDiv.innerHTML = `
        <i class="fas fa-hourglass-half" style="font-size: 2rem;"></i>
        <h3>Coming Soon!</h3>
        <p>📚 ${code}: ${name}</p>
        <p>${semester}${ordinal} Semester - ${session} 20${year} (${term === 'Mid' ? 'Midterm' : 'Final'})</p>
        <p>Question papers and notes will be available here shortly.</p>
        <button class="btn btn-primary" onclick="this.parentElement.remove()" style="margin-top: 1rem;">Close</button>
    `;

    const existingMsg = document.querySelector('.coming-soon-message');
    if (existingMsg) existingMsg.remove();

    const subjectsDisplay = document.getElementById('subjectsDisplayArea');
    subjectsDisplay.appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: 'smooth' });
}

// Faculty Page
function renderFacultyPage() {
    const container = document.getElementById('facultyContent');
    if (!getCurrentUser()) { container.innerHTML = `<div class="login-warning"><i class="fas fa-lock"></i><h3>Login Required</h3><button class="btn btn-primary" onclick="openModal(); showLoginForm();">Login Now</button></div>`; return; }
    container.innerHTML = `<div class="filter-container"><input type="text" id="searchInput" class="search-box" placeholder="🔍 Search faculty by name or email..."><div class="designation-filters"><label><input type="checkbox" value="All" checked onchange="filterFaculty()"> All Faculty</label><label><input type="checkbox" value="Professor" onchange="filterFaculty()"> Professor</label><label><input type="checkbox" value="Associate Professor" onchange="filterFaculty()"> Associate Professor</label><label><input type="checkbox" value="Assistant Professor" onchange="filterFaculty()"> Assistant Professor</label><label><input type="checkbox" value="Lecturer" onchange="filterFaculty()"> Lecturer</label></div></div><div id="facultyList" class="faculty-grid"></div>`;
    filterFaculty();
}

function filterFaculty() {
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const checks = document.querySelectorAll('.designation-filters input');
    let all = false, selected = [];
    checks.forEach(c => { if (c.checked && c.value === 'All') all = true; else if (c.checked && c.value !== 'All') selected.push(c.value); });
    let filtered = facultyData.filter(f => search === '' || f.name.toLowerCase().includes(search) || f.email.toLowerCase().includes(search));
    if (!all && selected.length) filtered = filtered.filter(f => selected.includes(f.position));
    const list = document.getElementById('facultyList');
    if (!filtered.length) { list.innerHTML = '<div class="no-results">No faculty members found</div>'; return; }
    list.innerHTML = filtered.map(f => `<div class="faculty-card"><h3>${f.name}</h3><div class="faculty-position">${f.position}</div><div class="faculty-email"><i class="fas fa-envelope"></i> <a href="mailto:${f.email}">${f.email}</a></div></div>`).join('');
}

window.filterFaculty = filterFaculty;
window.viewSubject = viewSubject;
window.selectSemester = selectSemester;
window.setFilter = setFilter;
window.fetchAndDisplayQuestions = fetchAndDisplayQuestions;
window.showComingSoon = showComingSoon;
window.showQuestionDetails = showQuestionDetails;
window.bookmarkQuestion = bookmarkQuestion;
window.removeBookmarkFromQuestion = removeBookmarkFromQuestion;
window.logQuestionView = logQuestionView;

// ============================================
// PAGE NAVIGATION
// ============================================
const authModal = document.getElementById('authModal');
function openModal() { authModal.style.display = 'block'; document.body.style.overflow = 'hidden'; authModal.scrollTop = 0; }
function closeModal() { authModal.style.display = 'none'; document.body.style.overflow = ''; }
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const icon = button.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        button.setAttribute('aria-label', 'Hide password');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        button.setAttribute('aria-label', 'Show password');
    }
}
function showLoginForm() { 
    document.getElementById('loginTab').classList.add('active'); 
    document.getElementById('signupTab').classList.remove('active'); 
    document.getElementById('loginForm').classList.add('active-form'); 
    document.getElementById('signupForm').classList.remove('active-form'); 
    document.getElementById('forgotPasswordForm').classList.remove('active-form');
    document.getElementById('resetPasswordForm').classList.remove('active-form');
}
function showSignupForm() { 
    document.getElementById('signupTab').classList.add('active'); 
    document.getElementById('loginTab').classList.remove('active'); 
    document.getElementById('signupForm').classList.add('active-form'); 
    document.getElementById('loginForm').classList.remove('active-form'); 
    document.getElementById('forgotPasswordForm').classList.remove('active-form');
    document.getElementById('resetPasswordForm').classList.remove('active-form');
}
function showForgotPasswordForm() {
    document.getElementById('loginForm').classList.remove('active-form');
    document.getElementById('signupForm').classList.remove('active-form');
    document.getElementById('forgotPasswordForm').classList.add('active-form');
    document.getElementById('resetPasswordForm').classList.remove('active-form');
}
function showResetPasswordForm() {
    document.getElementById('loginForm').classList.remove('active-form');
    document.getElementById('signupForm').classList.remove('active-form');
    document.getElementById('forgotPasswordForm').classList.remove('active-form');
    document.getElementById('resetPasswordForm').classList.add('active-form');
}

function hideAll() { ['homeSection', 'subjectsSection', 'facultySection', 'questionsSection', 'aboutSection', 'contactSection', 'adminSection', 'studentSection'].forEach(id => { const el = document.getElementById(id); if (el) el.style.display = 'none'; }); }
function setActive(idx) { document.querySelectorAll('.nav-links a').forEach((a, i) => { a.classList.remove('active'); }); const links = document.querySelectorAll('.nav-links a'); if (links[idx]) links[idx].classList.add('active'); }
function showHome() { if (getCurrentUser()) { showDashboard(); return; } hideAll(); document.getElementById('homeSection').style.display = 'block'; setActive(0); }
function showSubjects() { hideAll(); document.getElementById('subjectsSection').style.display = 'block'; renderSubjectsPage(); setActive(2); }
function showFaculty() { hideAll(); document.getElementById('facultySection').style.display = 'block'; renderFacultyPage(); setActive(3); }
function showQuestions() { hideAll(); document.getElementById('questionsSection').style.display = 'block'; renderQuestionsPage(); setActive(4); }
function showAbout() { hideAll(); document.getElementById('aboutSection').style.display = 'block'; setActive(5); }
function showContact() { hideAll(); document.getElementById('contactSection').style.display = 'block'; setActive(6); }

function setupProtectedCards() { document.querySelectorAll('[data-require-login="true"]').forEach(card => { card.addEventListener('click', () => { if (!getCurrentUser()) { showToast('Please login first!', 'error'); openModal(); } else showDashboard(); }); }); }

function showToast(message, type) { const c = document.getElementById('toastContainer'); const t = document.createElement('div'); const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' }; t.className = 'toast toast-' + (type || 'info'); t.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '"></i> ' + message; c.appendChild(t); setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; setTimeout(() => t.remove(), 300); }, 3000); }

// DASHBOARD
function showDashboard() { const user = getCurrentUser(); if (!user) { showToast('Please login first!', 'error'); openModal(); return; } hideAll(); setActive(0); if (user.role === 'admin') { document.getElementById('adminSection').style.display = 'block'; renderAdminOverview(); } else { document.getElementById('studentSection').style.display = 'block'; renderStudentProfile(); } }
function showLoaderThenDashboard() { const loader = document.getElementById('pageLoader'); if (loader) { loader.classList.remove('hidden'); setTimeout(() => { showDashboard(); loader.classList.add('hidden'); }, 1000); } else { showDashboard(); } }
function showAdminTab(tab) { document.querySelectorAll('#adminSection .dashboard-tab').forEach(t => t.classList.remove('active-tab')); document.querySelectorAll('#adminSection .sidebar-link').forEach(l => l.classList.remove('active')); const map = { overview: 'adminOverview', questions: 'adminQuestions', faculty: 'adminFaculty', users: 'adminUsers' }; document.getElementById(map[tab]).classList.add('active-tab'); if(event && event.target) { const link = event.target.closest('.sidebar-link'); if(link) link.classList.add('active'); } if (tab === 'overview') renderAdminOverview(); else if (tab === 'questions') renderAdminQuestions(); else if (tab === 'faculty') renderAdminFaculty(); else if (tab === 'users') renderAdminUsers(); }
function showStudentTab(tab) { document.querySelectorAll('#studentSection .dashboard-tab').forEach(t => t.classList.remove('active-tab')); document.querySelectorAll('#studentSection .sidebar-link').forEach(l => l.classList.remove('active')); const map = { profile: 'studentProfile', bookmarks: 'studentBookmarks', history: 'studentHistory' }; document.getElementById(map[tab]).classList.add('active-tab'); if(event && event.target) { const link = event.target.closest('.sidebar-link'); if(link) link.classList.add('active'); } if (tab === 'profile') renderStudentProfile(); else if (tab === 'bookmarks') renderStudentBookmarks(); else if (tab === 'history') renderStudentHistory(); }

// ============================================
// ADMIN FUNCTIONS (API INTEGRATED)
// ============================================

async function renderAdminOverview() { 
    adminOverview = await fetchAPI('overview/') || {};
    allQuestions = await fetchAPI('questions/') || [];
    
    document.getElementById('adminOverview').innerHTML = `
        <h2 class="dash-title"><i class="fas fa-tachometer-alt"></i> Admin Overview</h2>
        <div class="dash-cards">
            <div class="dash-card"><i class="fas fa-users"></i><span class="dash-number">${adminOverview.total_users || 0}</span><span class="dash-label">Users</span></div>
            <div class="dash-card"><i class="fas fa-file-alt"></i><span class="dash-number">${adminOverview.total_questions || 0}</span><span class="dash-label">Questions</span></div>
            <div class="dash-card"><i class="fas fa-chalkboard-teacher"></i><span class="dash-number">${adminOverview.total_faculty || 0}</span><span class="dash-label">Faculty</span></div>
            <div class="dash-card"><i class="fas fa-layer-group"></i><span class="dash-number">${adminOverview.total_semesters || 0}</span><span class="dash-label">Semesters</span></div>
        </div>
        <h3 style="margin-bottom:1rem;">Recent Uploads</h3>
        ${allQuestions.length === 0 ? '<div class="empty-state"><i class="fas fa-inbox"></i><p>No questions uploaded yet</p></div>' : 
        '<div class="question-list">' + allQuestions.slice(0, 5).map(q => `<div class="question-item"><div><span class="q-title">${q.course_name || 'Course'}</span><br><span class="q-meta">Semester ${q.semester_number} - ${q.term}</span></div></div>`).join('') + '</div>'}
    `; 
}

async function renderAdminQuestions() { 
    allQuestions = await fetchAPI('questions/') || [];
    let semOpts = ''; for (let i = 1; i <= 8; i++) semOpts += `<option value="${i}">Semester ${i}</option>`; 
    let yearOpts = ['26', '25', '24', '23', '22'].map(y => `<option value="${y}">20${y}</option>`).join(''); 
    
    document.getElementById('adminQuestions').innerHTML = `
        <h2 class="dash-title"><i class="fas fa-file-upload"></i> Upload Question Paper</h2>
        <div class="dash-form">
            <div class="form-group"><label>Semester</label><select id="qSemester" onchange="updateSubjectOptions()">${semOpts}</select></div>
            <div class="form-group"><label>Subject Code</label><select id="qSubject"></select></div>
            <div class="form-group"><label>Year</label><select id="qYear">${yearOpts}</select></div>
            <div class="form-group"><label>Session</label><select id="qSession"><option value="Autumn">Autumn</option><option value="Spring">Spring</option></select></div>
            <div class="form-group"><label>Term</label><select id="qTerm"><option value="Mid">Mid</option><option value="Final">Final</option></select></div>
            <div class="form-group"><label>Google Drive / PDF Link</label><input type="url" id="qLink" placeholder="https://drive.google.com/..." required></div>
            <div class="form-group"><label>Description (Optional)</label><input type="text" id="qDesc" placeholder="e.g., Final Exam, Midterm"></div>
            <button class="btn btn-primary" onclick="uploadQuestion()"><i class="fas fa-upload"></i> Upload</button>
        </div>
        <h3 style="margin-top:2rem;margin-bottom:1rem;">Uploaded Questions (${allQuestions.length})</h3>
        ${allQuestions.length === 0 ? '<div class="empty-state"><i class="fas fa-inbox"></i><p>No questions yet</p></div>' : 
        '<div class="question-list">' + allQuestions.map(q => `<div class="question-item"><div><span class="q-title">${q.course_code} - ${q.course_name}</span><br><span class="q-meta">Sem ${q.semester_number} - ${q.session} ${q.year} (${q.term})</span></div><div class="question-actions"><a href="${q.drive_link}" target="_blank" class="btn-sm btn-edit"><i class="fas fa-external-link-alt"></i></a><button class="btn-sm btn-delete" onclick="deleteQuestion(${q.id})"><i class="fas fa-trash"></i></button></div></div>`).join('') + '</div>'}
    `; 
    updateSubjectOptions(); 
}

function updateSubjectOptions() { 
    const sem = document.getElementById('qSemester').value; 
    const courses = semesterCourses[sem] || []; 
    // We need both the database course ID and display details
    // But since course IDs are positive integers in the database, we need to map course code to actual ID.
    // In our backend serializer, `Course` is serialized with its ID. Let's make sure our dropdown option values are the actual DB course IDs!
    // Wait, where do we get the database course ID?
    // In loadInitialData(), we fetched semesters, and each course has `id` in the backend but we mapped it to code/name/credit. Let's check loadInitialData().
    // Let's modify loadInitialData() to preserve the course ID!
    // Yes! Let's update loadInitialData() to include `id: c.id`. Then in updateSubjectOptions(), set the value to c.id.
    document.getElementById('qSubject').innerHTML = courses.map(c => `<option value="${c.id}">${c.code} - ${c.name}</option>`).join(''); 
}

// Modify loadInitialData to include course IDs
async function loadInitialDataWithIds() {
    const semesters = await fetchAPI('semesters/');
    if (semesters) {
        semesterCourses = {};
        semesters.forEach(sem => {
            semesterCourses[sem.number] = sem.courses.map(c => ({
                id: c.id,
                code: c.code,
                name: c.name,
                credit: c.credit_hours,
                prereq: c.prerequisite || '-'
            }));
        });
    }

    if (getCurrentUser()) {
        const faculty = await fetchAPI('faculty/');
        if (faculty) facultyData = faculty;
    }
}

// Re-assign loadInitialData to the one that preserves IDs
loadInitialData = loadInitialDataWithIds;

async function uploadQuestion() { 
    const sem = document.getElementById('qSemester').value; 
    const courseId = document.getElementById('qSubject').value; 
    const year = document.getElementById('qYear').value; 
    const session = document.getElementById('qSession').value; 
    const term = document.getElementById('qTerm').value; 
    const link = document.getElementById('qLink').value; 
    const desc = document.getElementById('qDesc').value || '';
    
    if (!link) { showToast('Please enter a link!', 'error'); return; } 
    
    const body = { course: parseInt(courseId), semester: parseInt(sem), year: year, session: session, term: term, drive_link: link, description: desc };
    const res = await fetchAPI('questions/', 'POST', body);
    
    if (res && res.id) {
        showToast('Question uploaded!', 'success'); 
        renderAdminQuestions();
    } else {
        showToast('Failed to upload', 'error');
    }
}

async function deleteQuestion(id) { 
    if (!confirm('Delete this question?')) return; 
    const res = await fetchAPI(`questions/${id}/`, 'DELETE');
    if (res) {
        showToast('Question deleted', 'info'); 
        renderAdminQuestions(); 
    }
}

async function renderAdminFaculty() { 
    const facultyList = await fetchAPI('faculty/') || [];
    const posOpts = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer'].map(p => `<option value="${p}">${p}</option>`).join(''); 
    
    document.getElementById('adminFaculty').innerHTML = `
        <h2 class="dash-title"><i class="fas fa-users-cog"></i> Manage Faculty</h2>
        <div class="dash-form" style="margin-bottom:2rem;">
            <h4 style="margin-bottom:1rem;">Add New Faculty</h4>
            <div class="form-group"><label>Name</label><input type="text" id="fName" placeholder="Full name"></div>
            <div class="form-group"><label>Position</label><select id="fPosition">${posOpts}</select></div>
            <div class="form-group"><label>Email</label><input type="email" id="fEmail" placeholder="email@example.com"></div>
            <button class="btn btn-primary" onclick="addFaculty()"><i class="fas fa-plus"></i> Add Faculty</button>
        </div>
        <h3 style="margin-bottom:1rem;">All Faculty (${facultyList.length})</h3>
        <div style="overflow-x:auto;">
            <table class="dash-table"><thead><tr><th>#</th><th>Name</th><th>Position</th><th>Email</th><th>Action</th></tr></thead>
            <tbody>${facultyList.map((f, i) => `<tr><td>${i + 1}</td><td>${f.name}</td><td>${f.position}</td><td>${f.email}</td><td><button class="btn-sm btn-delete" onclick="removeFaculty(${f.id}, '${f.name}')"><i class="fas fa-trash"></i></button></td></tr>`).join('')}</tbody></table>
        </div>`; 
}

async function addFaculty() { 
    const n = document.getElementById('fName').value.trim(); 
    const p = document.getElementById('fPosition').value; 
    const e = document.getElementById('fEmail').value.trim(); 
    if (!n || !e) { showToast('Name and email required!', 'error'); return; } 
    
    const res = await fetchAPI('faculty/', 'POST', { name: n, position: p, email: e });
    if (res && res.id) {
        showToast('Faculty added!', 'success'); 
        facultyData = await fetchAPI('faculty/');
        renderAdminFaculty();
    } else {
        showToast('Failed to add faculty', 'error');
    }
}

async function removeFaculty(id, name) { 
    if (!confirm(`Remove ${name}?`)) return; 
    const res = await fetchAPI(`faculty/${id}/`, 'DELETE');
    if (res) {
        showToast('Faculty removed', 'info'); 
        facultyData = await fetchAPI('faculty/');
        renderAdminFaculty(); 
    }
}

async function renderAdminUsers() { 
    const users = await fetchAPI('users/') || [];
    document.getElementById('adminUsers').innerHTML = `
        <h2 class="dash-title"><i class="fas fa-user-shield"></i> Registered Users</h2>
        <div style="overflow-x:auto;">
            <table class="dash-table"><thead><tr><th>#</th><th>Student ID</th><th>Email</th><th>Role</th></tr></thead>
            <tbody>${users.map((u, i) => `<tr><td>${i + 1}</td><td>${u.student_id}</td><td>${u.email}</td><td><span style="background:${u.role === 'admin' ? 'var(--danger)' : 'var(--secondary)'};color:white;padding:0.2rem 0.6rem;border-radius:var(--radius-full);font-size:0.75rem;">${u.role}</span></td></tr>`).join('')}</tbody></table>
        </div>`; 
}

// ============================================
// STUDENT DASHBOARD FUNCTIONS
// ============================================

async function renderStudentProfile() { 
    const user = getCurrentUser(); 
    if (!user) return; 

    // Retrieve latest security question status
    const profile = await fetchAPI('auth/me/');
    const displayUser = profile || user;

    document.getElementById('studentProfile').innerHTML = `
        <h2 class="dash-title"><i class="fas fa-id-card"></i> My Profile</h2>
        <div class="profile-card" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 2rem; max-width: 450px; text-align: center; box-shadow: var(--shadow-sm); margin: 1.5rem auto;">
            <i class="fas fa-user-circle profile-icon" style="font-size: 5rem; color: var(--primary); margin-bottom: 1rem; display: inline-block;"></i>
            <h2 style="font-size: 1.6rem; margin-bottom: 0.5rem;">Student ID: ${displayUser.studentId}</h2>
            <p style="color: var(--text-muted); margin-bottom: 0.5rem;"><i class="fas fa-envelope"></i> ${displayUser.email}</p>
            <p style="font-size: 0.95rem; margin-bottom: 1.2rem;">
                <strong>Security Question:</strong> 
                ${displayUser.security_question ? `<span style="color: var(--success);">${displayUser.security_question}</span>` : `<span style="color: var(--danger); font-style: italic;">Not set</span>`}
            </p>
            <span class="profile-role" style="background: var(--primary); color: white; padding: 0.3rem 1rem; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: bold; text-transform: uppercase;">STUDENT</span>
        </div>
    `; 
}

async function renderStudentBookmarks() { 
    const bookmarks = await fetchAPI('student/bookmarks/') || [];
    const container = document.getElementById('studentBookmarks');

    if (bookmarks.length === 0) {
        container.innerHTML = `
            <h2 class="dash-title"><i class="fas fa-bookmark"></i> My Bookmarks</h2>
            <div class="empty-state" style="text-align: center; padding: 3rem 1rem;">
                <i class="far fa-bookmark" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem;"></i>
                <p>You haven't bookmarked any question papers yet.</p>
                <button class="btn btn-primary" onclick="showQuestions()" style="margin-top: 1rem;">Browse Questions</button>
            </div>
        `;
        return;
    }

    let listHtml = bookmarks.map(b => {
        const q = b.question_paper_details;
        if (!q) return '';
        return `
            <div class="question-item">
                <div>
                    <span class="q-title"><strong>${q.course_code} - ${q.course_name}</strong></span><br>
                    <span class="q-meta">Semester ${q.semester_number} - ${q.term}</span>
                </div>
                <div class="question-actions">
                    <a href="${q.drive_link}" target="_blank" class="btn-sm btn-edit" onclick="logQuestionView(${q.id})"><i class="fas fa-external-link-alt"></i></a>
                    <button class="btn-sm btn-delete" onclick="removeBookmark(${q.question_paper})"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <h2 class="dash-title"><i class="fas fa-bookmark"></i> My Bookmarks (${bookmarks.length})</h2>
        <div class="question-list">
            ${listHtml}
        </div>
    `;
}

async function removeBookmark(questionPaperId) {
    if (!confirm('Remove this bookmark?')) return;
    const res = await fetchAPI(`student/bookmarks/${questionPaperId}/`, 'DELETE');
    if (res) {
        showToast('Bookmark removed', 'info');
        renderStudentBookmarks();
    }
}

async function renderStudentHistory() { 
    const history = await fetchAPI('student/history/') || [];
    const container = document.getElementById('studentHistory');

    if (history.length === 0) {
        container.innerHTML = `
            <h2 class="dash-title"><i class="fas fa-history"></i> Recent Activity</h2>
            <div class="empty-state" style="text-align: center; padding: 3rem 1rem;">
                <i class="fas fa-history" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem;"></i>
                <p>No recent activity found.</p>
            </div>
        `;
        return;
    }

    let listHtml = history.map(h => {
        const date = new Date(h.timestamp).toLocaleString();
        return `
            <div class="question-item" style="padding: 0.8rem 1rem;">
                <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <span class="activity-text"><i class="fas fa-info-circle" style="color: var(--primary); margin-right: 0.5rem;"></i>${h.action}</span>
                    <span class="q-meta" style="font-size: 0.75rem;"><i class="far fa-clock"></i> ${date}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <h2 class="dash-title"><i class="fas fa-history"></i> Recent Activity (${history.length})</h2>
        <div class="question-list">
            ${listHtml}
        </div>
    `;
}

// Password Reset Action Flow
async function getSecurityQuestion() {
    const ident = document.getElementById('forgotEmail').value.trim();
    if (!ident) {
        showToast('Please enter your email or Student ID', 'error');
        return;
    }
    const res = await fetchAPI(`auth/forgot-password/?identifier=${encodeURIComponent(ident)}`);
    if (res && res.security_question) {
        document.getElementById('resetIdentifier').value = ident;
        document.getElementById('displayQuestion').textContent = res.security_question;
        showResetPasswordForm();
    }
}

async function handlePasswordReset() {
    const ident = document.getElementById('resetIdentifier').value;
    const answer = document.getElementById('resetAnswer').value.trim();
    const newPass = document.getElementById('resetNewPassword').value;
    const confirmPass = document.getElementById('resetConfirmPassword').value;

    if (!answer || !newPass || !confirmPass) {
        showToast('Please fill all fields', 'error');
        return;
    }
    if (newPass !== confirmPass) {
        showToast('Passwords do not match', 'error');
        return;
    }
    if (newPass.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    const res = await fetchAPI('auth/reset-password/', 'POST', {
        identifier: ident,
        security_answer: answer,
        new_password: newPass
    });

    if (res && res.message) {
        showToast(res.message, 'success');
        showLoginForm();
    }
}

window.removeBookmark = removeBookmark;
window.getSecurityQuestion = getSecurityQuestion;
window.handlePasswordReset = handlePasswordReset;
window.showForgotPasswordForm = showForgotPasswordForm;
window.showResetPasswordForm = showResetPasswordForm;

// ============================================
// INITIALIZATION
// ============================================

async function init() {
    updateUI(); 
    setupProtectedCards();
    
    // Load data from Django Backend
    await loadInitialData();

    document.getElementById('loginBtn').addEventListener('click', () => { openModal(); showLoginForm(); });
    document.getElementById('signupBtn').addEventListener('click', () => { openModal(); showSignupForm(); });
    document.querySelector('.close-modal').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => { if (e.target === authModal) closeModal(); });
    
    document.getElementById('loginTab').addEventListener('click', showLoginForm);
    document.getElementById('signupTab').addEventListener('click', showSignupForm);
    document.getElementById('switchToSignup').addEventListener('click', (e) => { e.preventDefault(); showSignupForm(); });
    document.getElementById('switchToLogin').addEventListener('click', (e) => { e.preventDefault(); showLoginForm(); });
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    document.getElementById('loginForm').addEventListener('submit', async (e) => { 
        e.preventDefault(); 
        const res = await login(document.getElementById('loginEmail').value, document.getElementById('loginPassword').value); 
        const msg = document.getElementById('loginMessage'); 
        msg.textContent = res.message; 
        msg.className = 'auth-message ' + (res.success ? 'success-message' : 'error-message'); 
        if (res.success) setTimeout(() => { closeModal(); updateUI(); e.target.reset(); msg.className = 'auth-message'; showLoaderThenDashboard(); }, 1500); 
    });
    
    document.getElementById('signupForm').addEventListener('submit', async (e) => { 
        e.preventDefault(); 
        const sId = document.getElementById('signupStudentId').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const pass = document.getElementById('signupPassword').value;
        const confirmPass = document.getElementById('confirmPassword').value;
        const sQuest = document.getElementById('signupSecurityQuestion').value;
        const sAns = document.getElementById('signupSecurityAnswer').value.trim();

        if (pass !== confirmPass) {
            showToast('Passwords do not match!', 'error');
            return;
        }
        if (!sAns) {
            showToast('Please provide an answer to the security question!', 'error');
            return;
        }

        const res = await signup(sId, email, pass, sQuest, sAns);
        const msg = document.getElementById('signupMessage'); 
        msg.textContent = res.message; 
        msg.className = 'auth-message ' + (res.success ? 'success-message' : 'error-message'); 
        if (res.success) setTimeout(() => { showLoginForm(); e.target.reset(); msg.className = 'auth-message'; }, 2000);
    });

    if (getCurrentUser()) { showDashboard(); } else { showHome(); }
    setTimeout(() => { const loader = document.getElementById('pageLoader'); if (loader) loader.classList.add('hidden'); }, 800);
}

window.showHome = showHome; window.showSubjects = showSubjects; window.showFaculty = showFaculty; window.showQuestions = showQuestions; window.showAbout = showAbout; window.showContact = showContact; window.openModal = openModal; window.showLoginForm = showLoginForm;
window.showDashboard = showDashboard; window.showAdminTab = showAdminTab; window.showStudentTab = showStudentTab;
window.uploadQuestion = uploadQuestion; window.deleteQuestion = deleteQuestion; window.updateSubjectOptions = updateSubjectOptions;
window.addFaculty = addFaculty; window.removeFaculty = removeFaculty; 
window.showToast = showToast; window.toggleMobileMenu = toggleMobileMenu; window.navClick = navClick;

init();