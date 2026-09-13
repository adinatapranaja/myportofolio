# Generated manually to track the Project model.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('technologies', models.CharField(max_length=255)),
                ('project_url', models.URLField(blank=True)),
                ('repository_url', models.URLField(blank=True)),
            ],
        ),
    ]
