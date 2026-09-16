from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


@override_settings(ALLOWED_HOSTS=['testserver'])
class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title='Asisten Dosen PBP',
            description='Membangun aplikasi web yang aman dan responsif.',
            category='part-time',
        )
        self.project = Project.objects.create(
            title='Sistem Kehadiran Event',
            description='Platform kehadiran event dengan QR aman dan dashboard.',
            technologies='Django, Firebase, JavaScript',
            project_url='https://example.com/project',
            repository_url='https://github.com/adinatapranaja/project',
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"',
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get('/halaman-yang-tidak-ada/')

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), 'Asisten Dosen PBP')
        self.assertEqual(self.experience.category, 'part-time')
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse('main:show_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience.html')
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, 'Part-Time')
        self.assertContains(response, 'Sedang berlangsung')
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"',
        )

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, 'Belum ada pengalaman yang ditambahkan.')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse('main:show_experience'))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, 'Selesai')

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects.html')

    def test_projects_page_displays_data(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.technologies)
        self.assertContains(response, self.project.project_url)
        self.assertContains(response, self.project.repository_url)

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, 'Belum ada proyek yang ditambahkan.')

    def test_create_project_page_is_accessible(self):
        response = self.client.get(reverse('main:create_project'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_project.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_project_saves_valid_data(self):
        response = self.client.post(
            reverse('main:create_project'),
            {
                'title': 'Project Baru',
                'description': 'Deskripsi project baru.',
                'technologies': 'Django, Python',
                'project_url': '',
                'repository_url': '',
            },
        )

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertTrue(Project.objects.filter(title='Project Baru').exists())
