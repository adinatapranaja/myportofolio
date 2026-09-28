from django.urls import path

from main.views import (
    create_project,
    create_experience,
    delete_experience,
    delete_project,
    edit_experience,
    get_experiences_json,
    get_projects_json,
    login_user,
    logout_user,
    register,
    show_experience,
    show_main,
    show_projects,
)

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('experience/', show_experience, name='show_experience'),
    path('experience/add/', create_experience, name='create_experience'),
    path(
        'experience/<uuid:experience_id>/edit/',
        edit_experience,
        name='edit_experience',
    ),
    path(
        'experience/<uuid:experience_id>/delete/',
        delete_experience,
        name='delete_experience',
    ),
    path(
        'api/experiences/',
        get_experiences_json,
        name='get_experiences_json',
    ),
    path('projects/', show_projects, name='show_projects'),
    path('projects/add/', create_project, name='create_project'),
    path('api/projects/', get_projects_json, name='get_projects_json'),
    path(
        'projects/<uuid:project_id>/delete/',
        delete_project,
        name='delete_project',
    ),
]
