from django.shortcuts import redirect, render

from main.forms import ProjectForm
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
    }
    return render(request, 'index.html', context)


def show_experience(request):
    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'experience_list': Experience.objects.all(),
    }
    return render(request, 'experience.html', context)


def show_projects(request):
    context = {
        'name': 'Adinata Alaudin Pranaja',
        'short_name': 'Adinata',
        'project_list': Project.objects.all(),
    }
    return render(request, 'projects.html', context)


def create_project(request):
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
