from django import forms

from main.models import Project


class ProjectForm(forms.ModelForm):
    """Form untuk menambahkan data project ke database."""

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'technologies',
            'project_url',
            'repository_url',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Nama project'}),
            'description': forms.Textarea(
                attrs={'placeholder': 'Jelaskan project secara singkat', 'rows': 5}
            ),
            'technologies': forms.TextInput(
                attrs={'placeholder': 'Contoh: Django, PostgreSQL, JavaScript'}
            ),
            'project_url': forms.URLInput(
                attrs={'placeholder': 'https://contoh.com (opsional)'}
            ),
            'repository_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/... (opsional)'}
            ),
        }
