import json

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
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
        self.editor_group, _ = Group.objects.get_or_create(name='Editor')
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

    def test_ajax_create_experience_permissions_and_method(self):
        url = reverse('main:create_experience_ajax')
        count = Experience.objects.count()
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 403)
        self.assertIn('message', response.json())
        user = User.objects.create_user(username='ajax-user')
        self.client.force_login(user)
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        user.groups.add(self.editor_group)
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        self.assertEqual(Experience.objects.count(), count)

    def test_ajax_create_experience_validation_and_success(self):
        self.client.force_login(self.owner)
        url = reverse('main:create_experience_ajax')
        count = Experience.objects.count()
        data = {'title': '  ', 'description': 'AJAX experience', 'category': 'internship'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])
        data.update(title='AJAX experience', thumbnail='javascript:alert(1)')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('thumbnail', response.json()['errors'])
        self.assertEqual(Experience.objects.count(), count)
        data['thumbnail'] = 'https://example.com'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), count + 1)
        self.assertEqual(Experience.objects.get(pk=response.json()['pk']).title, data['title'])

    def test_ajax_create_experience_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse('main:create_experience_ajax')
        data = {'title': 'CSRF experience', 'description': 'Protected', 'category': 'internship'}
        count = Experience.objects.count()
        self.assertEqual(client.post(url, data).status_code, 403)
        self.assertEqual(Experience.objects.count(), count)
        client.get(reverse('main:show_experience'))
        response = client.post(url, data, HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 201)

    def test_ajax_create_project_permissions_and_method(self):
        url = reverse('main:create_project_ajax')
        count = Project.objects.count()
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 403)
        self.assertIn('message', response.json())
        user = User.objects.create_user(username='ajax-user')
        self.client.force_login(user)
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        user.groups.add(self.editor_group)
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        self.assertEqual(Project.objects.count(), count)

    def test_ajax_create_project_validation_and_success(self):
        self.client.force_login(self.owner)
        url = reverse('main:create_project_ajax')
        count = Project.objects.count()
        data = {'title': '  ', 'description': 'AJAX project', 'technologies': 'Django'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])
        data.update(title='AJAX project', project_url='javascript:alert(1)')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('project_url', response.json()['errors'])
        self.assertEqual(Project.objects.count(), count)
        data['project_url'] = 'https://example.com'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), count + 1)
        self.assertEqual(Project.objects.get(pk=response.json()['pk']).title, data['title'])

    def test_ajax_create_project_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse('main:create_project_ajax')
        data = {'title': 'CSRF project', 'description': 'Protected', 'technologies': 'Django'}
        count = Project.objects.count()
        self.assertEqual(client.post(url, data).status_code, 403)
        self.assertEqual(Project.objects.count(), count)
        client.get(reverse('main:show_projects'))
        response = client.post(url, data, HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 201)

    def test_experience_forms_reject_html_only_text(self):
        self.client.force_login(self.owner)
        count = Experience.objects.count()
        endpoints = [
            ('main:create_experience_ajax', [], 400),
            ('main:create_experience', [], 200),
            ('main:edit_experience', [self.experience.pk], 200),
        ]
        for field in ('title', 'description'):
            for endpoint, args, status in endpoints:
                with self.subTest(field=field, endpoint=endpoint):
                    data = {'title': 'Engineer', 'description': 'Build systems', 'category': 'internship'}
                    data[field] = '<img src="x" onerror="alert(1)">'
                    response = self.client.post(reverse(endpoint, args=args), data)
                    self.assertEqual(response.status_code, status)
                    errors = response.json()['errors'] if endpoint.endswith('_ajax') else response.context['form'].errors
                    self.assertIn(field, errors)
        self.assertEqual(Experience.objects.count(), count)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Asisten Dosen PBP')
        self.assertEqual(self.experience.description, 'Membangun aplikasi web yang aman dan responsif.')

    def test_experience_forms_strip_html_before_saving(self):
        self.client.force_login(self.owner)
        data = {
            'title': ' <b>Sanitized experience</b> ',
            'description': ' <p>Build <em>systems</em><img src="x" onerror="alert(1)"></p> ',
            'category': 'internship',
        }
        for endpoint, args, status in [
            ('main:create_experience_ajax', [], 201),
            ('main:create_experience', [], 302),
            ('main:edit_experience', [self.experience.pk], 302),
        ]:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(reverse(endpoint, args=args), data)
                self.assertEqual(response.status_code, status)
        cleaned = Experience.objects.filter(title='Sanitized experience')
        self.assertEqual(cleaned.count(), 3)
        for experience in cleaned:
            self.assertEqual(experience.description, 'Build systems')
            self.assertEqual(experience.category, 'internship')

    def test_project_forms_reject_html_only_titles(self):
        self.client.force_login(self.owner)
        data = {
            'title': '<img src="x" onerror="alert(1)">',
            'description': 'Description',
            'technologies': 'Django',
        }
        count = Project.objects.count()
        for endpoint, args, status in [
            ('main:create_project_ajax', [], 400),
            ('main:create_project', [], 200),
            ('main:edit_project', [self.project.pk], 200),
        ]:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(reverse(endpoint, args=args), data)
                self.assertEqual(response.status_code, status)
                if endpoint.endswith('_ajax'):
                    self.assertIn('title', response.json()['errors'])
                else:
                    self.assertIn('title', response.context['form'].errors)
        self.assertEqual(Project.objects.count(), count)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Sistem Kehadiran Event')

    def test_project_forms_strip_html_before_saving(self):
        self.client.force_login(self.owner)
        data = {
            'title': ' <b>Portfolio</b> ',
            'description': ' <p>Hello <em>world</em></p> ',
            'technologies': ' <strong>Django</strong> ',
        }
        for endpoint, args, status in [
            ('main:create_project_ajax', [], 201),
            ('main:create_project', [], 302),
            ('main:edit_project', [self.project.pk], 302),
        ]:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(reverse(endpoint, args=args), data)
                self.assertEqual(response.status_code, status)
        cleaned = Project.objects.filter(title='Portfolio')
        self.assertEqual(cleaned.count(), 3)
        for project in cleaned:
            self.assertEqual(project.description, 'Hello world')
            self.assertEqual(project.technologies, 'Django')

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

        self.assertRedirects(
            response,
            reverse('main:login'),
            fetch_redirect_response=False,
        )
        self.assertTrue(User.objects.filter(username='adinata-test').exists())

        login_response = self.client.get(reverse('main:login'))
        self.assertContains(login_response, 'Account created successfully. Please log in.')

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
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, 'id="experience-grid"')
        self.assertContains(response, 'js/experience.js')
        self.assertNotIn('experience_list', response.context)
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"',
        )

    def test_experience_ajax_shell_respects_roles_and_initial_search(self):
        user = User.objects.create_user(username='experience-shell-user')
        editor = User.objects.create_user(username='experience-shell-editor')
        editor.groups.add(self.editor_group)
        placeholder = '00000000-0000-0000-0000-000000000000'
        for account, can_star, can_edit, can_delete in [
            (None, False, False, False), (user, True, False, False),
            (editor, True, True, False), (self.owner, True, True, True),
        ]:
            with self.subTest(account=account):
                self.client.logout()
                if account:
                    self.client.force_login(account)
                response = self.client.get(reverse('main:show_experience'), {'title': 'Dosen'})
                html = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'value="Dosen"')
                self.assertEqual('id="experience-form"' in html, can_delete)
                self.assertContains(response, f'data-endpoint="{reverse("api:experience-list")}"')
                self.assertContains(response, reverse('api:experience-detail', args=[placeholder]))
                self.assertContains(response, reverse('api:experience-star', args=[placeholder]))
                self.assertContains(response, 'csrfmiddlewaretoken')
                self.assertIn('csrftoken', response.cookies)
                self.assertEqual('data-action="star"' in html, can_star)
                self.assertEqual('Login to star' in html, not can_star)
                self.assertEqual('data-action="edit"' in html, can_edit)
                self.assertEqual('id="experience-edit-form"' in html, can_edit)
                self.assertEqual('data-action="delete"' in html, can_delete)
                for legacy_url in [
                    reverse('main:edit_experience', args=[placeholder]),
                    reverse('main:get_experiences_json'),
                    reverse('main:toggle_experience_star', args=[placeholder]),
                    reverse('main:delete_experience', args=[placeholder]),
                    reverse('main:create_experience_ajax'),
                ]:
                    self.assertNotIn(f'"{legacy_url}"', html)

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, 'Belum ada pengalaman yang ditambahkan.')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse('main:show_experience'))

        self.assertFalse(self.experience.is_ongoing)
        payload = self.client.get(reverse('main:get_experiences_json')).json()
        fields = next(item['fields'] for item in payload if item['pk'] == str(self.experience.pk))
        self.assertFalse(fields['is_ongoing'])
        self.assertIsNotNone(fields['ended_at'])

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects.html')

    def test_projects_page_loads_data_via_ajax(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertNotContains(response, self.project.title)
        self.assertContains(response, 'id="projects-grid"')
        self.assertContains(response, f'data-endpoint="{reverse("api:project-list")}"')
        self.assertNotContains(response, reverse('main:get_projects_json'))
        self.assertContains(response, 'js/projects.js')
        self.assertNotIn('project_list', response.context)

    def test_projects_page_uses_drf_endpoints_for_each_role(self):
        user = User.objects.create_user(username='projects-shell-user')
        editor = User.objects.create_user(username='projects-shell-editor')
        editor.groups.add(self.editor_group)
        placeholder = '00000000-0000-0000-0000-000000000000'
        for account, can_star, can_edit, can_manage in [
            (None, False, False, False), (user, True, False, False),
            (editor, True, True, False), (self.owner, True, True, True),
        ]:
            with self.subTest(account=account):
                self.client.logout()
                if account:
                    self.client.force_login(account)
                response = self.client.get(reverse('main:show_projects'))
                html = response.content.decode()
                self.assertContains(response, reverse('api:project-detail', args=[placeholder]))
                self.assertContains(response, reverse('api:project-star', args=[placeholder]))
                self.assertContains(response, 'csrfmiddlewaretoken')
                self.assertIn('csrftoken', response.cookies)
                self.assertEqual('data-action="star"' in html, can_star)
                self.assertEqual('Login to star' in html, not can_star)
                self.assertEqual(reverse('main:edit_project', args=[placeholder]) in html, can_edit)
                self.assertEqual('data-action="delete"' in html, can_manage)
                self.assertEqual('id="project-form"' in html, can_manage)
                for legacy_url in [
                    reverse('main:toggle_star', args=[placeholder]),
                    reverse('main:delete_project', args=[placeholder]),
                    reverse('main:create_project_ajax'),
                ]:
                    self.assertNotIn(f'"{legacy_url}"', html)

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

    def test_editor_can_open_and_update_project(self):
        editor = User.objects.create_user(
            username='portfolio-editor',
            password='StrongPassword123!',
        )
        editor.groups.add(self.editor_group)
        self.client.force_login(editor)

        page_response = self.client.get(
            reverse('main:edit_project', args=[self.project.id]),
        )
        update_response = self.client.post(
            reverse('main:edit_project', args=[self.project.id]),
            {
                'title': 'Sistem Kehadiran yang Diperbarui',
                'description': 'Deskripsi setelah diperbarui oleh editor.',
                'technologies': 'Django, PostgreSQL',
                'project_url': 'https://example.com/updated-project',
                'repository_url': 'https://github.com/adinatapranaja/updated-project',
            },
        )

        self.assertEqual(page_response.status_code, 200)
        self.assertTemplateUsed(page_response, 'edit_project.html')
        self.assertRedirects(update_response, reverse('main:show_projects'))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Sistem Kehadiran yang Diperbarui')

    def test_regular_user_cannot_edit_project(self):
        user = User.objects.create_user(
            username='cannot-edit',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse('main:edit_project', args=[self.project.id]),
        )

        self.assertEqual(response.status_code, 403)

    def test_guest_is_redirected_when_opening_project_edit_page(self):
        response = self.client.get(
            reverse('main:edit_project', args=[self.project.id]),
        )

        self.assertRedirects(
            response,
            f'{reverse("main:login")}?next={reverse("main:edit_project", args=[self.project.id])}',
        )

    def test_editor_sees_edit_control_without_owner_controls(self):
        editor = User.objects.create_user(
            username='editor-controls',
            password='StrongPassword123!',
        )
        editor.groups.add(self.editor_group)
        self.client.force_login(editor)

        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(
            response,
            reverse('main:edit_project', args=['00000000-0000-0000-0000-000000000000']),
        )
        self.assertNotContains(response, reverse('main:create_project'))
        self.assertNotContains(response, 'data-action="delete"')

    def test_create_experience_page_is_accessible(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('main:create_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_experience.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_experience_saves_valid_data(self):
        self.client.force_login(self.owner)
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

    def test_experience_star_and_personalized_json(self):
        url = reverse('main:toggle_experience_star', args=[self.experience.pk])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 0)
        user = User.objects.create_user(username='experience-reader')
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 1)
        self.experience.starred_by.add(user)
        self.assertEqual(self.experience.starred_by.count(), 1)

        def fields():
            return next(item['fields'] for item in self.client.get(
                reverse('main:get_experiences_json')).json()
                if item['pk'] == str(self.experience.pk))

        data = fields()
        self.assertTrue(data['is_starred'])
        self.assertEqual(data['star_count'], 1)
        self.assertEqual(data['starred_by_names'], user.username)
        self.assertEqual(data['category_display'], 'Part-Time')
        self.assertTrue(data['is_ongoing'])
        self.client.logout()
        self.assertFalse(fields()['is_starred'])
        self.assertEqual(fields()['star_count'], 1)
        self.client.force_login(user)
        self.client.post(url)
        self.assertEqual(fields()['star_count'], 0)

    def test_experience_star_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse('main:toggle_experience_star', args=[self.experience.pk])
        self.assertEqual(client.post(url).status_code, 403)
        self.assertEqual(self.experience.starred_by.count(), 0)
        client.get(reverse('main:show_experience'))
        self.assertEqual(client.post(url, HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value).status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 1)

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
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse('main:edit_experience', args=[self.experience.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_experience.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_edit_experience_updates_data(self):
        self.client.force_login(self.owner)
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
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse('main:delete_experience', args=[self.experience.id]),
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_removes_data(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('main:delete_experience', args=[self.experience.id]),
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_editor_can_update_experience(self):
        editor = User.objects.create_user(
            username='experience-editor',
            password='StrongPassword123!',
        )
        editor.groups.add(self.editor_group)
        self.client.force_login(editor)

        response = self.client.post(
            reverse('main:edit_experience', args=[self.experience.id]),
            {
                'title': 'Updated Teaching Assistant',
                'description': 'Pengalaman diperbarui oleh editor.',
                'category': 'part-time',
                'thumbnail': '',
            },
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Updated Teaching Assistant')

    def test_regular_user_cannot_manage_experiences(self):
        user = User.objects.create_user(
            username='experience-user',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        create_response = self.client.get(reverse('main:create_experience'))
        edit_response = self.client.get(
            reverse('main:edit_experience', args=[self.experience.id]),
        )
        delete_response = self.client.post(
            reverse('main:delete_experience', args=[self.experience.id]),
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_guest_is_redirected_when_managing_experience(self):
        response = self.client.get(reverse('main:create_experience'))

        self.assertRedirects(
            response,
            f'{reverse("main:login")}?next={reverse("main:create_experience")}',
        )

    def test_projects_json_returns_serialized_projects(self):
        response = self.client.get(reverse('main:get_projects_json'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = json.loads(response.content)
        titles = [project['fields']['title'] for project in payload]
        self.assertIn(self.project.title, titles)

    def test_projects_json_uses_username_instead_of_user_id_for_stars(self):
        user = User.objects.create_user(
            username='api-stargazer',
            password='StrongPassword123!',
        )
        self.project.starred_by.add(user)

        response = self.client.get(reverse('main:get_projects_json'))

        payload = json.loads(response.content)
        project_data = next(
            item for item in payload if item['fields']['title'] == self.project.title
        )
        self.assertEqual(project_data['fields']['starred_by'], [[user.username]])

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

    def test_projects_page_preserves_initial_search_for_ajax(self):
        response = self.client.get(
            reverse('main:show_projects'),
            {'title': 'Kehadiran'},
        )

        self.assertContains(response, 'value="Kehadiran"')
        self.assertNotContains(response, self.project.title)

    def test_projects_json_reports_star_state_for_current_user(self):
        self.project.starred_by.add(self.owner)
        endpoint = reverse('main:get_projects_json')

        def fields():
            return next(item['fields'] for item in self.client.get(endpoint).json()
                        if item['pk'] == str(self.project.pk))

        anonymous = fields()
        self.assertEqual(anonymous['star_count'], 1)
        self.assertFalse(anonymous['is_starred'])
        self.assertEqual(anonymous['starred_by_names'], self.owner.username)
        self.client.force_login(self.owner)
        self.assertTrue(fields()['is_starred'])
        self.project.starred_by.remove(self.owner)
        unstarred = fields()
        self.assertFalse(unstarred['is_starred'])
        self.assertEqual(unstarred['star_count'], 0)

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
