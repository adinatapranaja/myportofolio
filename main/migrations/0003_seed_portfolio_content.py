from datetime import datetime, timezone

from django.db import migrations


EXPERIENCE_TITLES = [
    'Founder, President Director & CTO - PandaTech',
    'Full Stack Developer - Capstone Project',
    'Full Stack Developer - Kementerian Sekretariat Negara RI',
]


def seed_portfolio_content(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Project = apps.get_model('main', 'Project')

    Experience.objects.get_or_create(
        title=EXPERIENCE_TITLES[0],
        defaults={
            'category': 'full-time',
            'description': (
                'September 2025 - Present | Jakarta. Memimpin visi teknologi, '
                'arsitektur, strategi produk, dan pengembangan end-to-end untuk '
                'solusi web modern, automasi berbasis AI, serta UI/UX berpusat '
                'pada pengguna di PandaTech.'
            ),
        },
    )
    Experience.objects.get_or_create(
        title=EXPERIENCE_TITLES[1],
        defaults={
            'category': 'freelance',
            'description': (
                'June 2025 - Present | Jakarta. Mengembangkan platform manajemen '
                'event dengan QR code aman, AES encryption, HMAC validation, '
                'single-use token, pelacakan kehadiran real-time, Camera API, '
                'Firebase, dan dashboard analitik responsif.'
            ),
        },
    )
    Experience.objects.get_or_create(
        title=EXPERIENCE_TITLES[2],
        defaults={
            'category': 'full-time',
            'description': (
                'August 2025 - January 2026 | Jakarta. Membangun sistem informasi '
                'manajemen personel yang aman menggunakan PHP, MySQL, REST API, '
                'role-based access control, document management, serta dashboard '
                'admin responsif.'
            ),
            'ended_at': datetime(2026, 1, 31, tzinfo=timezone.utc),
        },
    )
    Project.objects.get_or_create(
        title='Secure Event Attendance Platform',
        defaults={
            'description': (
                'Platform manajemen event untuk QR code aman, scanning dan '
                'pelacakan kehadiran real-time, bulk guest import/export, '
                'notifikasi penyelenggara, dashboard analitik, serta manajemen '
                'multi-user administrator.'
            ),
            'technologies': (
                'React.js, Context API, Firebase Authentication, Firestore, '
                'Firebase Realtime Database, AES Encryption, HMAC, Camera API, PWA'
            ),
        },
    )


def remove_seeded_portfolio_content(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Project = apps.get_model('main', 'Project')

    Experience.objects.filter(title__in=EXPERIENCE_TITLES).delete()
    Project.objects.filter(title='Secure Event Attendance Platform').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_project'),
    ]

    operations = [
        migrations.RunPython(seed_portfolio_content, remove_seeded_portfolio_content),
    ]
