from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class StarredModelSerializer(serializers.ModelSerializer):
    """Adds read-only star fields for models with a ``starred_by`` relation.

    The values are computed from ``starred_by.all()`` so a queryset that uses
    ``prefetch_related('starred_by')`` needs no extra query per object.
    """

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ', '.join(user.username for user in obj.starred_by.all())


class ProjectSerializer(StarredModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'technologies',
            'project_url', 'repository_url',
            'star_count', 'is_starred', 'starred_by_names',
        ]
        read_only_fields = ['id']

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError('Title cannot be empty.')
        return value

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate_technologies(self, value):
        return strip_tags(value).strip()


class ExperienceSerializer(StarredModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Experience
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'thumbnail', 'started_at', 'ended_at', 'is_ongoing',
            'star_count', 'is_starred', 'starred_by_names',
        ]
        read_only_fields = ['id', 'started_at', 'ended_at']

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError('Title cannot be empty.')
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError('Description cannot be empty.')
        return value
