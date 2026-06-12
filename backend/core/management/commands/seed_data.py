"""
Management command to seed the database with initial data:
- 8 Semesters + all courses
- 62 faculty members
- 1 admin user
"""
from django.core.management.base import BaseCommand
from core.models import User, Semester, Course, Faculty


SEMESTER_COURSES = {
    1: [
        {"code": "CSE-1121", "name": "Computer Programming I", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-1122", "name": "Computer Programming I Lab", "credit": 1.5, "prereq": "-"},
        {"code": "EEE-1121", "name": "Basic Electrical Engineering", "credit": 3.0, "prereq": "-"},
        {"code": "EEE-1122", "name": "Basic Electrical Engineering Lab", "credit": 1.5, "prereq": "-"},
        {"code": "MATH-1107", "name": "Mathematics I (Differential and Integral Calculus)", "credit": 3.0, "prereq": "-"},
        {"code": "PHY-1101", "name": "Physics I (Mechanics, Waves, Heat and Thermodynamics)", "credit": 3.0, "prereq": "-"},
        {"code": "UREL-1106", "name": "Advanced English", "credit": 2.0, "prereq": "-"},
        {"code": "UREM-1101", "name": "Text of Ethics and Morality", "credit": 1.0, "prereq": "-"},
    ],
    2: [
        {"code": "CSE-1221", "name": "Computer Programming II", "credit": 3.0, "prereq": "CSE-1121"},
        {"code": "CSE-1222", "name": "Computer Programming II Lab", "credit": 1.5, "prereq": "-"},
        {"code": "CSE-1223", "name": "Discrete Mathematics", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-1230", "name": "Competitive Programming I", "credit": 1.0, "prereq": "-"},
        {"code": "EEE-1221", "name": "Electronics", "credit": 3.0, "prereq": "EEE-1121"},
        {"code": "EEE-1222", "name": "Electronics Lab", "credit": 1.5, "prereq": "-"},
        {"code": "MATH-1207", "name": "Mathematics II (Geometry and Differential Equations)", "credit": 3.0, "prereq": "MATH-1107"},
        {"code": "PHY-1201", "name": "Physics II (Electromagnetism, Optics and Modern Physics)", "credit": 3.0, "prereq": "PHY-1101"},
        {"code": "PHY-1204", "name": "Physics II Lab", "credit": 1.5, "prereq": "-"},
        {"code": "URED-1201", "name": "Basic Principles of Islam", "credit": 2.0, "prereq": "-"},
    ],
    3: [
        {"code": "CHEM-2301", "name": "Chemistry", "credit": 3.0, "prereq": "-"},
        {"code": "CHEM-2304", "name": "Chemistry Lab", "credit": 1.5, "prereq": "-"},
        {"code": "CSE-2321", "name": "Data Structures", "credit": 3.0, "prereq": "CSE-1121"},
        {"code": "CSE-2322", "name": "Data Structures Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-2323", "name": "Digital Logic Design", "credit": 3.0, "prereq": "EEE-1121"},
        {"code": "CSE-2324", "name": "Digital Logic Design Lab", "credit": 1.5, "prereq": "-"},
        {"code": "CSE-2340", "name": "Software Development I", "credit": 2.0, "prereq": "CSE-1221"},
        {"code": "MATH-2307", "name": "Mathematics III (Matrices, Linear System of Equations and Vector Analysis)", "credit": 3.0, "prereq": "MATH-1207"},
        {"code": "STAT-2311", "name": "Probability and Statistics", "credit": 2.0, "prereq": "-"},
        {"code": "URED-2302", "name": "Sciences of Quran and Hadith", "credit": 1.0, "prereq": "-"},
        {"code": "URED-2305", "name": "Comparative Religion", "credit": 3.0, "prereq": "-"},
    ],
    4: [
        {"code": "CSE-2421", "name": "Computer Algorithms", "credit": 3.0, "prereq": "CSE-2321"},
        {"code": "CSE-2422", "name": "Computer Algorithms Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-2423", "name": "Database Management Systems", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-2424", "name": "Database Management Systems Lab", "credit": 1.5, "prereq": "-"},
        {"code": "CSE-2425", "name": "Theory of Computing", "credit": 2.0, "prereq": "-"},
        {"code": "CSE-2430", "name": "Competitive Programming II", "credit": 1.0, "prereq": "-"},
        {"code": "EEE-2421", "name": "Electrical Drives and Instrumentation", "credit": 2.0, "prereq": "EEE-1221"},
        {"code": "EEE-2422", "name": "Electrical Drives and Instrumentation Lab", "credit": 1.0, "prereq": "-"},
        {"code": "GEBL-2401", "name": "Bangla Language and Literature", "credit": 2.0, "prereq": "-"},
        {"code": "MATH-2407", "name": "Mathematics IV (Complex Variable, Fourier Analysis and Z-transform)", "credit": 3.0, "prereq": "MATH-2307"},
        {"code": "ME-2412", "name": "Engineering Drawing Lab", "credit": 1.0, "prereq": "-"},
        {"code": "ACC-2401", "name": "Financial and Managerial Accounting", "credit": 2.0, "prereq": "-"},
    ],
    5: [
        {"code": "CSE-3521", "name": "Computer Architecture", "credit": 3.0, "prereq": "CSE-2323"},
        {"code": "CSE-3523", "name": "Microprocessors, Microcontrollers and Embedded Systems", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-3524", "name": "Microprocessors, Microcontrollers and Embedded Systems Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-3525", "name": "Data Communication", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-3527", "name": "Compiler", "credit": 3.0, "prereq": "CSE-2425"},
        {"code": "CSE-3528", "name": "Compiler Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-3529", "name": "Systems Analysis and Design", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-3532", "name": "Tools and Technologies for Internet Programming", "credit": 2.0, "prereq": "CSE-1222"},
        {"code": "URED-3503", "name": "Political Thoughts and Social Behavior", "credit": 1.0, "prereq": "-"},
    ],
    6: [
        {"code": "CSE-3631", "name": "Operating Systems", "credit": 3.0, "prereq": "CSE-3521"},
        {"code": "CSE-3632", "name": "Operating Systems Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-3633", "name": "Computer Networks", "credit": 3.0, "prereq": "CSE-3525"},
        {"code": "CSE-3634", "name": "Computer Networks Lab", "credit": 1.5, "prereq": "-"},
        {"code": "CSE-3635", "name": "Artificial Intelligence", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-3636", "name": "Artificial Intelligence Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-3637", "name": "Software Engineering", "credit": 3.0, "prereq": "CSE-3529"},
        {"code": "CSE-3638", "name": "Software Engineering Lab", "credit": 0.75, "prereq": "-"},
        {"code": "CSE-3640", "name": "Software Development II Lab", "credit": 0.75, "prereq": "CSE-3532"},
        {"code": "URED-3604", "name": "Life and Teachings of Prophet Muhammad (SAAS)", "credit": 1.0, "prereq": "-"},
        {"code": "GEHE-3601", "name": "History of the Emergence of Bangladesh", "credit": 2.0, "prereq": "-"},
    ],
    7: [
        {"code": "CSE-4708", "name": "Field Work", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4741", "name": "Computer Graphics", "credit": 3.0, "prereq": "MATH-2307"},
        {"code": "CSE-4742", "name": "Computer Graphics Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4743", "name": "Computer Security", "credit": 2.0, "prereq": "-"},
        {"code": "CSE-4744", "name": "Computer Security Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4745", "name": "Numerical Methods", "credit": 2.0, "prereq": "CSE-1121"},
        {"code": "CSE-4746", "name": "Numerical Methods Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4747", "name": "Mathematical Analysis for Computer Science", "credit": 3.0, "prereq": "STAT-2311"},
        {"code": "CSE-4750", "name": "Technical Writing and Presentation", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4800", "name": "Project / Thesis", "credit": 4.0, "prereq": "-"},
        {"code": "ECON-3501", "name": "Principles of Economics", "credit": 2.0, "prereq": "-"},
        {"code": "URIH-4701", "name": "A Survey of Islamic History and Culture", "credit": 1.0, "prereq": "-"},
    ],
    8: [
        {"code": "CSE-4805", "name": "Social, Professional and Ethical Issues in Computing", "credit": 2.0, "prereq": "-"},
        {"code": "CSE-4819", "name": "Special Topic on Computer Science and Engineering", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-4820", "name": "Special Topic on Computer Science and Engineering Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4822", "name": "General Viva", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4823", "name": "Fault Tolerant System", "credit": 3.0, "prereq": "CSE-3521"},
        {"code": "CSE-4824", "name": "Fault Tolerant System Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4825", "name": "Basic Graph Theory", "credit": 3.0, "prereq": "CSE-2321"},
        {"code": "CSE-4826", "name": "Basic Graph Theory Lab", "credit": 1.0, "prereq": "-"},
        {"code": "CSE-4827", "name": "Simulation and Modeling", "credit": 3.0, "prereq": "-"},
        {"code": "CSE-4828", "name": "Simulation and Modeling Lab", "credit": 1.0, "prereq": "-"},
    ],
}

FACULTY_DATA = [
    {"name": "Prof. Dr. Md. Monirul Islam", "position": "Professor", "email": "monirliton@yahoo.com"},
    {"name": "Prof. Mohammed Shamsul Alam", "position": "Professor", "email": "alam_cse@yahoo.com"},
    {"name": "Prof. Dr. Abu Naser Md. Rezaul Karim", "position": "Professor", "email": "zakianaser@yahoo.com"},
    {"name": "Mahadi Hassan", "position": "Associate Professor", "email": "mahadi_cse@yahoo.com"},
    {"name": "Tanveer Ahsan", "position": "Associate Professor", "email": "tanveer@iiuc.ac.bd"},
    {"name": "Dr. Mohammad Aman Ullah", "position": "Associate Professor", "email": "ullah047@yahoo.com"},
    {"name": "Dr. Mohammad Manjur Alam", "position": "Associate Professor", "email": "manjuralam44@yahoo.com"},
    {"name": "Md. Mahiuddin", "position": "Associate Professor", "email": "mmuict@gmail.com"},
    {"name": "Zinia Sultana Mukti", "position": "Associate Professor", "email": "zinniaiiuc@yahoo.com"},
    {"name": "Md. Khaliluzzaman", "position": "Associate Professor", "email": "khalilcse021@gmail.com"},
    {"name": "Md. Rashedul Islam", "position": "Associate Professor", "email": "rashed_maths@yahoo.com"},
    {"name": "Mohammed Safiullah", "position": "Associate Professor", "email": "safiullah@gmail.com"},
    {"name": "Abdullahil Kafi", "position": "Assistant Professor", "email": "abkafi@gmail.com"},
    {"name": "Dr. Siddique Ahmed", "position": "Assistant Professor", "email": "drsiddiqueahmed@gmail.com"},
    {"name": "Subrina Akter", "position": "Assistant Professor", "email": "subrina.a30@gmail.com"},
    {"name": "Saifur Rahman", "position": "Assistant Professor", "email": "saifurcubd@gmail.com"},
    {"name": "Shayhan Ameen Chowdhury", "position": "Assistant Professor", "email": "shayhan.ameen@gmail.com"},
    {"name": "ABM Yasir Arafat", "position": "Assistant Professor", "email": "abmya89@yahoo.com"},
    {"name": "Mohammad Sazid Zaman Khan", "position": "Assistant Professor", "email": "szkhanctg@gmail.com"},
    {"name": "Saiful Islam", "position": "Assistant Professor", "email": "engsaiful0@gmail.com"},
    {"name": "Farzana Tasnim", "position": "Assistant Professor", "email": "faranatasnim34@gmail.com"},
    {"name": "Muhammad Mizanur Rahman Mizan", "position": "Lecturer", "email": "mizaanrahman32@gmail.com"},
    {"name": "Sanjida Sharmin", "position": "Lecturer", "email": "ssharmin114@gmail.com"},
    {"name": "Israt Binteh Habib", "position": "Lecturer", "email": "israthabib.cse@gmail.com"},
    {"name": "Muhammed Nazmul Arefin", "position": "Lecturer", "email": "nazmul.muhammed.arefin@gmail.com"},
    {"name": "Jamil As-ad", "position": "Lecturer", "email": "jamilasad1@gmail.com"},
    {"name": "Nuren Nafisa", "position": "Lecturer", "email": "nurennafisa@gmail.com"},
    {"name": "Md. Badiuzzaman Biplob", "position": "Lecturer", "email": "biplob.cse45@gmail.com"},
    {"name": "Md. Monir Hossain", "position": "Lecturer", "email": "monir.cu.math1@gmail.com"},
    {"name": "Md Aminul Islam", "position": "Lecturer", "email": "taminulislam@gmail.com"},
    {"name": "Khandaker Tayef Shahriar", "position": "Lecturer", "email": "tayef@iiuc.ac.bd"},
    {"name": "Sahariar Reza", "position": "Lecturer", "email": "Sahariarp@gmail.com"},
    {"name": "Sabrina Jahan Maisha", "position": "Lecturer", "email": "sjbm1996@gmail.com"},
    {"name": "Asmaul Hosna Sadika", "position": "Lecturer", "email": "asmaulhosnasadika@gmail.com"},
    {"name": "Muhammad Mubinur Rahman", "position": "Lecturer", "email": "mubinlikhon@gmail.com"},
    {"name": "Rayhanuzzaman", "position": "Lecturer", "email": "rayhanuzzamanr@gmail.com"},
    {"name": "Ayesha Julekha", "position": "Lecturer", "email": "safinserain@gmail.com"},
    {"name": "Mr. Muhammad Nazim Uddin", "position": "Lecturer", "email": "nazimhabib77@gmail.com"},
    {"name": "Nowshin Tabassum", "position": "Lecturer", "email": "tabassum.nowshin1330@gmail.com"},
    {"name": "Mujibur Rahman Maruf", "position": "Lecturer", "email": "Mujiburmaruf.cuet17@gmail.com"},
    {"name": "Mahir Shadid", "position": "Lecturer", "email": "mahir.shadid@gmail.com"},
    {"name": "Miskatul Jannat", "position": "Lecturer", "email": "miskat@iiuc.ac.bd"},
    {"name": "Abdul Aziz", "position": "Lecturer", "email": "aziz.abdul.cu@gmail.com"},
    {"name": "Sauda Adiv Hanum", "position": "Lecturer", "email": "adivhanum@gmail.com"},
    {"name": "Sultana Tasnim Jahan", "position": "Lecturer", "email": "tasnim047sultana@gmail.com"},
    {"name": "Siam Sharif Ami", "position": "Lecturer", "email": "siamsharifami@gmail.com"},
    {"name": "Md Nazmul Hasan", "position": "Lecturer", "email": "nazmul122@iiuc.ac.bd"},
    {"name": "Ms. Khadiza Sultana Sayma", "position": "Lecturer", "email": "sayma.khadiza@gmail.com"},
    {"name": "Nurul Absar", "position": "Lecturer", "email": "nurulabsar.cse.cu@gmail.com"},
    {"name": "Monir Hossain", "position": "Lecturer", "email": "monirho.cse@gmail.com"},
    {"name": "Ashfaq Mahmud Fahim", "position": "Lecturer", "email": "u1904072@student.cuet.ac.bd"},
    {"name": "Monir Ahmad", "position": "Lecturer", "email": "ahmad.csecu@gmail.com"},
    {"name": "Md. Sadman Hafiz", "position": "Lecturer", "email": "hafiz.sust333@gmail.com"},
    {"name": "Timam Bin Saif Tahmid", "position": "Lecturer", "email": "timambinsaif462@gmail.com"},
    {"name": "Saif Sabbir", "position": "Lecturer", "email": "saifsabbir2k18@gmail.com"},
    {"name": "Raisa Nuzhat", "position": "Lecturer", "email": "raisa.csecu@gmail.com"},
    {"name": "Md Mirajul Islam", "position": "Lecturer", "email": "mirajulphysics@gmail.com"},
    {"name": "Mohammad Ariful Islam", "position": "Lecturer", "email": "arifislam928374@gmail.com"},
    {"name": "Md Nazmus Sajid", "position": "Lecturer", "email": "md.nazmus.sajid94@gmail.com"},
    {"name": "Fathema Tuj Johora", "position": "Lecturer", "email": "fathemsmrity123@gmail.com"},
    {"name": "Mohammad Sakif Ibn Yousuf", "position": "Lecturer", "email": "mdsakif98@gmail.com"},
]


class Command(BaseCommand):
    help = 'Seed the database with semesters, courses, faculty, and admin user'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(student_id='ADMIN-001').exists():
            User.objects.create_superuser(
                username='admin',
                student_id='ADMIN-001',
                email='admin@notenest.com',
                password='admin123',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('[SUCCESS] Admin user created (admin@notenest.com / admin123)'))
        else:
            self.stdout.write('Admin user already exists, skipping.')

        if not User.objects.filter(student_id='CSE-100').exists():
            User.objects.create_user(
                username='CSE-100',
                student_id='CSE-100',
                email='student@notenest.com',
                password='student123',
                role='student',
                security_question='What is your favorite subject?',
                security_answer='Computer Science',
            )
            self.stdout.write(self.style.SUCCESS('[SUCCESS] Dummy student created (CSE-100 / student123)'))
        else:
            self.stdout.write('Dummy student already exists, skipping.')

        # Create semesters and courses
        ordinals = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th"}
        course_count = 0
        for sem_num, courses in SEMESTER_COURSES.items():
            semester, created = Semester.objects.get_or_create(
                number=sem_num,
                defaults={'label': f"{ordinals[sem_num]} Semester"}
            )
            for c in courses:
                _, c_created = Course.objects.get_or_create(
                    code=c['code'],
                    defaults={
                        'name': c['name'],
                        'credit_hours': c['credit'],
                        'prerequisite': c['prereq'],
                        'semester': semester,
                    }
                )
                if c_created:
                    course_count += 1

        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] 8 semesters, {course_count} new courses seeded'))

        # Create faculty
        faculty_count = 0
        for f in FACULTY_DATA:
            _, created = Faculty.objects.get_or_create(
                email=f['email'],
                defaults={'name': f['name'], 'position': f['position']}
            )
            if created:
                faculty_count += 1

        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] {faculty_count} new faculty members seeded'))
        self.stdout.write(self.style.SUCCESS('[SUCCESS] Database seeding complete!'))
