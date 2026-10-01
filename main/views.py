from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def show_main(request):
    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'npm': '2506656356',
        'study_program': 'S1 Sistem Informasi',
        'bio': (
            'Full Stack Developer | Purwadhika Graduate | '
            'University of Indonesia Information Systems Student'
        ),
        'last_login': request.COOKIES.get('last_login'),
    }
    return render(request, 'index.html', context)


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name='Editor').exists()


def can_edit_portfolio(user):
    return user.is_superuser or is_editor(user)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('main:login')

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'form': form,
    }
    return render(request, 'register.html', context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        response = redirect('main:show_main')
        response.set_cookie(
            'last_login',
            timezone.now().strftime('%d %B %Y, %H:%M'),
        )
        return response

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'form': form,
    }
    return render(request, 'login.html', context)


def logout_user(request):
    if request.method == 'POST':
        logout(request)

    response = redirect('main:show_main')
    response.delete_cookie('last_login')
    return response


def show_experience(request):
    json_response = get_experiences_json(request)
    experiences = serializers.deserialize(
        'json',
        json_response.content.decode('utf-8'),
    )

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'experience_list': [experience.object for experience in experiences],
        'is_editor': is_editor(request.user),
    }
    return render(request, 'experience.html', context)


@login_required(login_url='/login/')
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:show_experience')
    else:
        form = ExperienceForm()

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'form': form,
    }
    return render(request, 'create_experience.html', context)


@login_required(login_url='/login/')
def edit_experience(request, experience_id):
    if not can_edit_portfolio(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('main:show_experience')
    else:
        form = ExperienceForm(instance=experience)

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'experience': experience,
        'form': form,
    }
    return render(request, 'edit_experience.html', context)


def get_experiences_json(request):
    title_query = request.GET.get('title', '').strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize('json', experiences)
    return HttpResponse(experiences_json, content_type='application/json')


@login_required(login_url='/login/')
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == 'POST':
        experience.delete()

    return redirect('main:show_experience')


def show_projects(request):
    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'title_query': request.GET.get('title', '').strip(),
        'is_editor': is_editor(request.user),
        'card_project': {'id': '00000000-0000-0000-0000-000000000000', 'title': ''},
        'form': ProjectForm() if request.user.is_superuser else None,
    }
    return render(request, 'projects.html', context)


@login_required(login_url='/login/')
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:show_projects')
    else:
        form = ProjectForm()

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'form': form,
    }
    return render(request, 'create_project.html', context)


@login_required(login_url='/login/')
def edit_project(request, project_id):
    if not can_edit_portfolio(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('main:show_projects')
    else:
        form = ProjectForm(instance=project)

    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'project': project,
        'form': form,
    }
    return render(request, 'edit_project.html', context)


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        data.append({
            'model': 'main.project',
            'pk': str(project.pk),
            'fields': {
                'title': project.title,
                'description': project.description,
                'technologies': project.technologies,
                'project_url': project.project_url,
                'repository_url': project.repository_url,
                'starred_by': [[user.username] for user in starred_users],
                'star_count': len(starred_users),
                'is_starred': request.user.is_authenticated and request.user in starred_users,
                'starred_by_names': ', '.join(user.username for user in starred_users),
            },
        })
    return JsonResponse(data, safe=False)


@login_required(login_url='/login/')
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project.delete()

    return redirect('main:show_projects')


@login_required(login_url='/login/')
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect('main:show_projects')
