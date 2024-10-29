from Tools.scripts.cleanfuture import verbose
from rest_framework import serializers
from ..models import Request, Task, Approve, RequestTemplate
from . import TaskSerializer, ApproveSerializer, CommentSerializer

class CreateRequestSerializer(serializers.ModelSerializer):
    # request_template  - is not required

    class Meta:
        model = Request
        fields = ['title', 'description', 'request_template']

    def create(self, validated_data):
        request_template_id = validated_data.pop('request_template', None)
        # Создаем заявку
        request_instance = Request.objects.create(**validated_data)
        if request_template_id:
            template = RequestTemplate.objects.get(id=request_template_id)
            # Копируем задачи из шаблона заявки
            for task in template.tasks.all():
                Task.objects.create(
                    on_request=request_instance,
                    title=task.title,
                    description=task.description,
                    dedlin_date=task.dedlin_date,
                    executor=task.executor,
                    status=task.status,
                )
            # Копируем согласования из шаблона заявки
            for approve in template.approves.all():
                Approve.objects.create(
                    on_request=request_instance,
                    title=approve.title,
                    description=approve.description,
                    coordinating=approve.coordinating,
                    status=approve.status,
                )

        return request_instance


class DetailRequestSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    approves = ApproveSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date',
                  'request_template', 'status', 'tasks', 'approves', 'comments']
        read_only_fields = ['id', 'tasks', 'approves', 'comments']


class ListRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date',
                  'request_template', 'status']
        read_only_fields = ['id', 'tasks', 'approves', 'comments']

class AppointRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date', 'request_template', 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'title', 'description', 'dedlin_date', 'request_template', 'created_at', 'updated_at', 'status']