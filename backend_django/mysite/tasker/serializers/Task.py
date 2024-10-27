from rest_framework import serializers
from django.utils import timezone
from ..models import Task, TaskTemplate, Request
from .TaskTemplate import TaskTemplateSerializer
from  .Comment import CommentSerializer
from mysite.serializers import GroupSerializer
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
    comments = CommentSerializer(many=True, read_only=True)
    group = GroupSerializer(read_only=True, required=False)
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
            'comments',
        ]
        read_only_fields = [
            'id',
            'closed_at',
            'dedlin_date',
            'cansel_date',
            'author',
            'status',
            'comments',
            'group',
            'executor',
        ]


class CreateTaskSerializer(serializers.ModelSerializer):
    task_template = serializers.IntegerField(write_only=True, required=False)
    on_request = serializers.IntegerField(write_only=True, required=False)
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'author',
            'task_template',
            'on_request',
        ]
        read_only_fields = [
            'id',
            'author'
        ]

    def create(self, validated_data):
        task_template_id = validated_data.pop('task_template', None)
        request_id = validated_data.pop('on_request', None)
        task_instance = Task.objects.create(**validated_data)
        if task_template_id:
            template = TaskTemplate.objects.get(id=task_template_id)
            if template:
                dedlin_date = timezone.now() + template.dedlin
                task_instance.dedlin_date = dedlin_date
                task_instance.group = template.group
                task_instance.task_template = template
        if request_id:
            request = Request.objects.get(id=request_id)
            task_instance.on_request = request
        task_instance.save()
        return task_instance


class AuthorUpdateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
        ]