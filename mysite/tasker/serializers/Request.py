from django.utils import timezone
from rest_framework import serializers


from ..models import Request, Task, Approve, RequestTemplate
from . import TaskSerializer, ApproveSerializer, CommentSerializer

class CreateRequestSerializer(serializers.ModelSerializer):
    # request_template  - is not required

    class Meta:
        model = Request
        fields = ['title', 'description', 'request_template']

    def create(self, validated_data):
        request_template = validated_data.get('request_template', None)

        request_instance = Request.objects.create(**validated_data)
        if request_template:
            request_instance.dedlin_date = timezone.now()+request_template.dedlin
            request_instance.group = request_template.group
            for task_template in request_template.tasks.all():
                Task.objects.create(
                    title=task_template.title,
                    description=task_template.description,
                    dedlin_date=timezone.now()+task_template.dedlin,
                    status= 'new',
                    group=task_template.group,
                    task_template= task_template,
                    on_request=request_instance
                )
            # Копируем согласования из шаблона заявки
            for approve_step in request_template.approval_route.steps.all():
                approve_data = {
                    'title': approve_step.title,
                    'order_number': approve_step.order_number,
                    'on_request': request_instance,
                    'status': 'new',
                }
                if approve_step.approval_type == 'specific':
                    approve_data['coordinating'] = approve_step.specific_approver
                elif approve_step.approval_type == 'group':
                    approve_data['group'] = approve_step.group
                elif approve_step.approval_type == 'manager':
                    approve_data['coordinating'] = validated_data['author'].manager

                Approve.objects.create(
                    **approve_data
                )

        return request_instance


class DetailRequestSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    approves = ApproveSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date',
                  'request_template', 'status', 'tasks', 'approves', 'comments',
                  'closed_at', 'created_at']
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