from django.db import migrations


def create_dummy_student(apps, schema_editor):
    User = apps.get_model('core', 'User')
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


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_questionpaper_session_questionpaper_year_and_more'),
    ]

    operations = [
        migrations.RunPython(create_dummy_student),
    ]
