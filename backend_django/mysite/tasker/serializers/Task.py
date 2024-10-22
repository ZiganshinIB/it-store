from rest_framework import serializers
from ..models import Task
from . import TaskTemplateSerializer
from djoser.conf import settings


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'closed_at',
            'dedlin_date',
            'cansel_date',
            'author',
            'executor',
            'status',
            'group',
            'task_template',
            'on_request',
        ]
        read_only_fields = [
            'id',
            'closed_at',
            'cansel_date',
            'author',
            'status',
        ]





class DetailTaskSerializer(serializers.ModelSerializer):
    author = settings.SERIALIZERS.current_user(read_only=True)
    executor = settings.SERIALIZERS.current_user(read_only=True)
    task_template = TaskTemplateSerializer(read_only=True, required=False)
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'closed_at',
            'dedlin_date',
            'cansel_date',
            'author',
            'executor',
            'status',
            'group',
            'task_template',
            'on_request',
        ]
        read_only_fields = [
            'id',
            'closed_at',
            'cansel_date',
            'author',
            'status',
        ]