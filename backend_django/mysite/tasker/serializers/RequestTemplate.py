from rest_framework import serializers
from ..models import RequestTemplate, TaskTemplate, ApprovalRoute
from . import TaskTemplateSerializer, DetailApprovalRouteSerializer


class ListRequestTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTemplate
        fields = [
            'id',
            'title',
            'description',
            'image',
            'dedlin',
            'approval_route',
            'complexity',
            'group',
        ]
        read_only_fields = [
            'id',
        ]


class DetailRequestTemplateSerializer(serializers.ModelSerializer):
    tasks = TaskTemplateSerializer(many=True, required=False)
    approval_route = DetailApprovalRouteSerializer(read_only=True, required=False)
    class Meta:
        model = RequestTemplate
        fields = [
            'id',
            'title',
            'description',
            'image',
            'dedlin',
            'approval_route',
            'complexity',
            'group',
            'tasks'
        ]
        read_only_fields = ['id', 'tasks', 'approval_route']


class CreateRequestTemplateSerializer(serializers.ModelSerializer):
    tasks = serializers.ListField(child=serializers.IntegerField(), required=False)
    approval_route = serializers.IntegerField(required=False)

    class Meta:
        model = RequestTemplate
        fields = [
            'id',
            'title',
            'description',
            'image',
            'dedlin',
            'tasks',
            'approval_route',
            'complexity',
            'group'
        ]
        read_only_fields = ['id',]

    def validate_tasks(self, value):
        if len(value) == 0:
            return value
        count = TaskTemplate.objects.filter(id__in=value).count()
        if count != len(value):
            raise serializers.ValidationError("Задачи с такими идентификаторами не существуют")
        return value

    def validate_approval_route(self, value):
        if value is not None:
            if not ApprovalRoute.objects.filter(id=value).exists():
                raise serializers.ValidationError("Маршрут согласования не существует")
        return value

    def create(self, validated_data):
        tasks = None
        approval_route = None
        if validated_data.get('tasks') is not None:
            tasks_ids = validated_data.pop('tasks')
            tasks = TaskTemplate.objects.filter(id__in=tasks_ids)
        if validated_data.get('approval_route') is not None:
            approval_route_id = validated_data.pop('approval_route')
            approval_route = ApprovalRoute.objects.get(id=approval_route_id)
        request = RequestTemplate.objects.create(**validated_data)
        if tasks is not None:
            request.tasks.set(tasks)
        if approval_route is not None:
            request.approval_route = approval_route
        request.save()
        return request


class UpdateRequestTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTemplate
        fields = [
            'id',
            'title',
            'description',
            'image',
            'dedlin',
            'tasks',
            'approval_route',
            'complexity',
            'group'
        ]
        read_only_fields = ['id', 'tasks', 'approval_route', 'group']


class AppendTaskTemplateSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()

    def validate_task_id(self, value):
        if not TaskTemplate.objects.filter(id=value).exists():
            raise serializers.ValidationError("Задача с таким идентификатором не существует")
        return value


