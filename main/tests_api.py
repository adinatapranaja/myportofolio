import uuid

from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, APITestCase, force_authenticate

from main.models import Experience, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly


@api_view(['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def editor_protected_view(request):
    return Response(status=status.HTTP_204_NO_CONTENT)


@override_settings(ALLOWED_HOSTS=['testserver'])
class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username='owner', password='test-password', email='owner@example.com',
        )
        self.visitor = User.objects.create_user(username='visitor', password='test-password')
        # Migration 0003 seeds portfolio projects, so counts are compared to this baseline.
        Project.objects.all().delete()
        self.project = Project.objects.create(
            title='Portfolio', description='My website', technologies='Django',
        )
        self.list_url = reverse('api:project-list')
        self.detail_url = reverse('api:project-detail', args=[self.project.id])
        self.star_url = reverse('api:project-star', args=[self.project.id])
        self.payload = {
            'title': 'New project', 'description': 'A useful app', 'technologies': 'Python',
            'project_url': 'https://example.com/', 'repository_url': '',
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], str(self.project.id))
        self.assertFalse(response.data[0]['is_starred'])
        self.assertNotIn('fields', response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {'title': 'PORT'})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {'title': 'not-found'})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse('api:project-detail', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {'title': 'Changed'}, format='json').status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Portfolio')

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data['id']).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({'title': '   '}, 'title'),
            ({'title': '<img src="x" onerror="alert(1)">'}, 'title'),
            ({'project_url': 'javascript:alert(1)'}, 'project_url'),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, 'My website')
        response = self.client.put(self.detail_url, {'title': 'Incomplete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, 'star_count': 99, 'is_starred': True,
            'starred_by_names': 'forged', 'starred_by': [self.visitor.id],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name='Editor'))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username='owner', password='test-password'))
        response = client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username='owner', password='test-password')
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies['csrftoken'].value
        response = client.post(
            self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PortfolioEditorPermissionTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        editor_group = Group.objects.create(name='Editor')
        self.owner = User.objects.create_superuser(username='owner', password='test-password')
        self.visitor = User.objects.create_user(username='visitor', password='test-password')
        self.editor = User.objects.create_user(username='editor', password='test-password')
        self.editor.groups.add(editor_group)
        self.staff = User.objects.create_user(username='staff', password='test-password', is_staff=True)

    def status_for(self, user, method):
        request = getattr(self.factory, method.lower())('/editor-protected/', {}, format='json')
        if user is not None:
            force_authenticate(request, user=user)
        return editor_protected_view(request).status_code

    def test_roles_follow_editor_permission_matrix(self):
        allowed = status.HTTP_204_NO_CONTENT
        denied = status.HTTP_403_FORBIDDEN
        matrix = {
            None: {'read': allowed, 'POST': denied, 'PUT': denied, 'PATCH': denied, 'DELETE': denied},
            'visitor': {'read': allowed, 'POST': denied, 'PUT': denied, 'PATCH': denied, 'DELETE': denied},
            'staff': {'read': allowed, 'POST': denied, 'PUT': denied, 'PATCH': denied, 'DELETE': denied},
            'editor': {'read': allowed, 'POST': denied, 'PUT': allowed, 'PATCH': allowed, 'DELETE': denied},
            'owner': {'read': allowed, 'POST': allowed, 'PUT': allowed, 'PATCH': allowed, 'DELETE': allowed},
        }
        for role, expected in matrix.items():
            user = getattr(self, role) if role else None
            for method in ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(role=role, method=method):
                    want = expected['read'] if method in ('GET', 'HEAD', 'OPTIONS') else expected[method]
                    self.assertEqual(self.status_for(user, method), want)

    def test_editor_needs_the_exact_group_name(self):
        self.visitor.groups.add(Group.objects.create(name='editor'))
        self.assertEqual(self.status_for(self.visitor, 'PATCH'), status.HTTP_403_FORBIDDEN)


@override_settings(ALLOWED_HOSTS=['testserver'])
class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username='owner', password='test-password', email='owner@example.com',
        )
        self.visitor = User.objects.create_user(
            username='visitor', password='test-password', email='visitor@example.com',
        )
        self.editor = User.objects.create_user(username='editor', password='test-password')
        self.editor.groups.add(Group.objects.create(name='Editor'))
        # Migration 0003 seeds portfolio experiences, so counts are compared to this baseline.
        Experience.objects.all().delete()
        self.experience = Experience.objects.create(
            title='Asisten Dosen PBP', description='Membangun aplikasi web.', category='part-time',
        )
        self.list_url = reverse('api:experience-list')
        self.detail_url = reverse('api:experience-detail', args=[self.experience.id])
        self.star_url = reverse('api:experience-star', args=[self.experience.id])
        self.payload = {
            'title': 'Backend Intern', 'description': 'Building internal APIs.',
            'category': 'internship', 'thumbnail': 'https://example.com/intern.jpg',
        }

    def assert_unchanged(self):
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Asisten Dosen PBP')
        self.assertEqual(self.experience.description, 'Membangun aplikasi web.')

    def test_public_list_detail_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item['id'], str(self.experience.id))
        self.assertEqual(item['category_display'], 'Part-Time')
        self.assertTrue(item['is_ongoing'])
        self.assertFalse(item['is_starred'])
        self.assertEqual(self.client.get(self.detail_url).data['title'], 'Asisten Dosen PBP')
        self.assertEqual(len(self.client.get(self.list_url, {'title': 'DOSEN'}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {'title': 'not-found'}).data, [])

    def test_missing_experience_returns_404(self):
        url = reverse('api:experience-detail', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
                self.assertEqual(self.client.patch(self.detail_url, {'title': 'Changed'}, format='json').status_code, 403)
                self.assertEqual(self.client.put(self.detail_url, self.payload, format='json').status_code, 403)
                self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
                self.assert_unchanged()

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_unchanged()

        response = self.client.patch(self.detail_url, {'title': 'Teaching Assistant'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Teaching Assistant')
        self.assertEqual(self.experience.description, 'Membangun aplikasi web.')

        response = self.client.put(self.detail_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.category, 'internship')

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data['id'], title='Backend Intern').exists())

        response = self.client.put(self.detail_url, {'title': 'Incomplete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.patch(self.detail_url, {'category': 'research'}, format='json').status_code, 200)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b'')
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_validation_rejects_bad_input(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({'title': '   '}, 'title'),
            ({'title': '<img src="x" onerror="alert(1)">'}, 'title'),
            ({'description': '<b></b>'}, 'description'),
            ({'thumbnail': 'javascript:alert(1)'}, 'thumbnail'),
            ({'category': 'astronaut'}, 'category'),
        ]:
            with self.subTest(field=field, changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assert_unchanged()

    def test_text_is_stripped_and_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload,
            'title': ' <b>Clean title</b> ', 'description': '<p>Build <em>APIs</em></p>',
            'star_count': 99, 'is_starred': True, 'starred_by': [self.visitor.id],
            'ended_at': '2001-01-01T00:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data['id'])
        self.assertEqual(created.title, 'Clean title')
        self.assertEqual(created.description, 'Build APIs')
        self.assertEqual(created.starred_by.count(), 0)
        self.assertIsNone(created.ended_at)
        self.assertEqual(response.data['star_count'], 0)
        self.assertFalse(response.data['is_starred'])

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(self.star_url, {'user': self.owner.id}, format='json')
        self.assertTrue(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 1)
        self.assertEqual(list(self.experience.starred_by.all()), [self.visitor])

        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.data['star_count'], 2)
        self.assertEqual(response.data['starred_by_names'], 'visitor, editor')

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 1)

    def test_response_hides_sensitive_account_data(self):
        self.experience.starred_by.add(self.visitor)
        content = self.client.get(self.list_url).content.decode()
        self.assertNotIn('visitor@example.com', content)
        self.assertNotIn('password', content)
        self.assertNotIn('pbkdf2', content)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username='owner', password='test-password'))
        self.assertEqual(client.post(self.list_url, self.payload, format='json').status_code, 403)
        self.assertEqual(client.patch(self.detail_url, {'title': 'Changed'}, format='json').status_code, 403)
        self.assertEqual(client.delete(self.detail_url).status_code, 403)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        self.assert_unchanged()
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username='editor', password='test-password')
        client.get(reverse('main:show_experience'))
        token = client.cookies['csrftoken'].value
        response = client.patch(
            self.detail_url, {'title': 'Updated with CSRF'}, format='json', HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Updated with CSRF')
