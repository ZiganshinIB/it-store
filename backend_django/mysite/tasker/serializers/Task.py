from rest_framework import serializers
from ..models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'closed_at', 'dedlin_date', 'cansel_date',
            'author', 'executor', 'status', 'group', 'task_template',
            'on_request', 'comments'
        ]
        read_only_fields = ['id', 'closed_at', 'cansel_date', 'author', 'status', 'comments']