import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


@override_settings(ALLOWED_HOSTS=['testserver'])
class MainTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username='portfolio-owner',
            password='StrongPassword123!',
        )
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

    def test_register_page_is_accessible(self):
        response = self.client.get(reverse('main:register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_register_creates_user(self):
        response = self.client.post(
            reverse('main:register'),
            {
                'username': 'adinata-test',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            },
        )

        self.assertRedirects(response, reverse('main:login'))
        self.assertTrue(User.objects.filter(username='adinata-test').exists())

    def test_login_page_is_accessible(self):
        response = self.client.get(reverse('main:login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_login_authenticates_user(self):
        User.objects.create_user(
            username='adinata-login',
            password='StrongPassword123!',
        )

        response = self.client.post(
            reverse('main:login'),
            {
                'username': 'adinata-login',
                'password': 'StrongPassword123!',
            },
        )

        self.assertRedirects(response, reverse('main:show_main'))
        self.assertIn('last_login', response.cookies)
        self.assertEqual(self.client.get(reverse('main:show_main')).wsgi_request.user.username, 'adinata-login')

    def test_home_displays_last_login_cookie(self):
        response = self.client.get(
            reverse('main:show_main'),
            HTTP_COOKIE='last_login=28 September 2026, 10:00',
        )

        self.assertContains(response, 'Last login: 28 September 2026, 10:00')

    def test_navbar_shows_register_and_login_for_guest(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertContains(response, 'Register')
        self.assertContains(response, 'Login')
        self.assertNotContains(response, 'Logout')

    def test_logout_ends_authenticated_session(self):
        user = User.objects.create_user(
            username='adinata-logout',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('main:logout'))

        self.assertRedirects(response, reverse('main:show_main'))
        self.assertIn('last_login', response.cookies)
        self.assertEqual(response.cookies['last_login']['max-age'], 0)
        response = self.client.get(reverse('main:show_main'))
        self.assertNotContains(response, 'Hi, adinata-logout')
        self.assertContains(response, 'Login')

    def test_navbar_shows_username_and_logout_for_authenticated_user(self):
        user = User.objects.create_user(
            username='adinata-navbar',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('main:show_main'))

        self.assertContains(response, 'Hi, adinata-navbar')
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, 'Register')

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
        self.client.force_login(self.owner)
        response = self.client.get(reverse('main:create_project'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_project.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_project_saves_valid_data(self):
        self.client.force_login(self.owner)
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

    def test_create_experience_page_is_accessible(self):
        response = self.client.get(reverse('main:create_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_experience.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_experience_saves_valid_data(self):
        response = self.client.post(
            reverse('main:create_experience'),
            {
                'title': 'Backend Developer Intern',
                'description': 'Membangun layanan backend untuk aplikasi internal.',
                'category': 'internship',
                'thumbnail': 'https://example.com/experience.jpg',
            },
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertTrue(
            Experience.objects.filter(title='Backend Developer Intern').exists()
        )

    def test_experiences_json_returns_serialized_experiences(self):
        response = self.client.get(reverse('main:get_experiences_json'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content)
        titles = [experience['fields']['title'] for experience in payload]
        self.assertIn(self.experience.title, titles)

    def test_experiences_json_filters_by_title(self):
        Experience.objects.create(
            title='Product Designer',
            description='Merancang antarmuka produk.',
            category='part-time',
        )

        response = self.client.get(
            reverse('main:get_experiences_json'),
            {'title': 'Asisten Dosen'},
        )

        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['fields']['title'], self.experience.title)

    def test_edit_experience_page_is_accessible(self):
        response = self.client.get(
            reverse('main:edit_experience', args=[self.experience.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_experience.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_edit_experience_updates_data(self):
        response = self.client.post(
            reverse('main:edit_experience', args=[self.experience.id]),
            {
                'title': 'Teaching Assistant PBP',
                'description': 'Mengembangkan materi dan membantu praktikum.',
                'category': 'part-time',
                'thumbnail': 'https://example.com/pbp.jpg',
            },
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Teaching Assistant PBP')
        self.assertEqual(self.experience.thumbnail, 'https://example.com/pbp.jpg')

    def test_delete_experience_requires_post(self):
        response = self.client.get(
            reverse('main:delete_experience', args=[self.experience.id]),
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_removes_data(self):
        response = self.client.post(
            reverse('main:delete_experience', args=[self.experience.id]),
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_projects_json_returns_serialized_projects(self):
        response = self.client.get(reverse('main:get_projects_json'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content)
        titles = [project['fields']['title'] for project in payload]
        self.assertIn(self.project.title, titles)

    def test_projects_json_filters_by_title(self):
        Project.objects.create(
            title='Portfolio Lain',
            description='Project kedua.',
            technologies='Python',
        )

        response = self.client.get(
            reverse('main:get_projects_json'),
            {'title': 'Kehadiran'},
        )

        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['fields']['title'], self.project.title)

    def test_projects_page_filters_by_title(self):
        response = self.client.get(
            reverse('main:show_projects'),
            {'title': 'Kehadiran'},
        )

        self.assertContains(response, self.project.title)
        self.assertNotContains(response, 'Secure Event Attendance Platform')

    def test_delete_project_requires_post(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse('main:delete_project', args=[self.project.id]),
        )

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_removes_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('main:delete_project', args=[self.project.id]),
        )

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_guest_is_redirected_when_opening_project_management_page(self):
        response = self.client.get(reverse('main:create_project'))

        self.assertRedirects(
            response,
            f'{reverse("main:login")}?next={reverse("main:create_project")}',
        )

    def test_regular_user_cannot_create_or_delete_projects(self):
        user = User.objects.create_user(
            username='regular-user',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        create_response = self.client.get(reverse('main:create_project'))
        delete_response = self.client.post(
            reverse('main:delete_project', args=[self.project.id]),
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_project_star_can_be_toggled_by_authenticated_user(self):
        user = User.objects.create_user(
            username='star-user',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        first_response = self.client.post(
            reverse('main:toggle_star', args=[self.project.id]),
        )
        self.assertRedirects(first_response, reverse('main:show_projects'))
        self.assertTrue(self.project.starred_by.filter(pk=user.pk).exists())

        second_response = self.client.post(
            reverse('main:toggle_star', args=[self.project.id]),
        )
        self.assertRedirects(second_response, reverse('main:show_projects'))
        self.assertFalse(self.project.starred_by.filter(pk=user.pk).exists())

    def test_guest_is_redirected_when_starring_project(self):
        response = self.client.post(
            reverse('main:toggle_star', args=[self.project.id]),
        )

        self.assertRedirects(
            response,
            f'{reverse("main:login")}?next={reverse("main:toggle_star", args=[self.project.id])}',
        )
