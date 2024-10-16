from rest_framework import serializers
from .models import ApprovalRoute, ApproveStep
from .models import RequestTemplate, RequestTaskRelation, TaskTemplate
from .models import Request, Task, Approve, Comment


class ApproveStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApproveStep
        fields = ['title', 'approval_type', 'specific_approver', 'group_approver', 'dedlin']
        read_only_fields = ['order_number', 'route']

    def validate(self, data):
        if data['approval_type'] == 'group' and not data['group_approver']:
            raise serializers.ValidationError("Укажите группу")
        if data['approval_type'] == 'specific' and not data['specific_approver']:
            raise serializers.ValidationError("Укажите согласователя")
        return data

class ApprovalRouteSerializer(serializers.ModelSerializer):
    steps = ApproveStepSerializer(many=True)
    class Meta:
        model = ApprovalRoute
        fields = ['title', 'description', 'author', 'steps']
        readline_only_fields = ['author']


    def create(self, validated_data):
        """
        Создание маршрута согласования
        :param validated_data: Данные для создания маршрута согласования
        :return:
        """
        steps_data = validated_data.pop('steps')
        approval_route = ApprovalRoute.objects.create(**validated_data)
        for i, step_data in enumerate(steps_data):
            ApproveStep.objects.create(order_number=i+1, route=approval_route, **step_data)
        return approval_route


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'title', 'description', 'dedline', 'complexity']
        read_only_fields = ['id']


class RequestTaskRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTaskRelation
        fields = ['request', 'task', 'additional_info']


class RequestTemplateSerializer(serializers.ModelSerializer):
    tasks = TaskTemplateSerializer(many=True, required=False)
    class Meta:
        model = RequestTemplate
        fields = ['id', 'title', 'description', 'image', 'dedline', 'approval_route', 'tasks']

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

class ApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approve
        fields = ['id', 'title', 'description', 'status']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id','created_at', 'author', 'updated_at']

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


class ListRequestSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    approves = ApproveSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date',
                  'request_template', 'status', 'tasks', 'approves', 'comments']

class AppointRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'title', 'description', 'group', 'executor', 'dedlin_date', 'request_template', 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'title', 'description', 'dedlin_date', 'request_template', 'created_at', 'updated_at', 'status']


# class RequestSerializer(serializers.ModelSerializer):
#     request_template = RequestTemplateSerializer(read_only=True)
#     class Meta:
#         model = Request
#         fields = ['id', 'title', 'description', 'image', 'dedline', 'approval_route', 'request_template', 'requester', 'status']
#
#
# class TaskSerializer(serializers.ModelSerializer):
#     request = RequestSerializer(read_only=True)
#     template = TaskTemplateSerializer(read_only=True)
#     class Meta:
#         model = Task
#         fields = ['id', 'title', 'description', 'dedline', 'complexity']