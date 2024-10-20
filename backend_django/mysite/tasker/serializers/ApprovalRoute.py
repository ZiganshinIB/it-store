from rest_framework import serializers
from ..models import ApprovalRoute, ApproveStep

class ApproveStepSerializer(serializers.ModelSerializer):
    """
    Сериализация шага согласования
    """
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

class ListApprovalRouteSerializer(serializers.ModelSerializer):
    """
    Общая сериализация маршрута согласования
    """
    class Meta:
        model = ApprovalRoute
        fields = ['id', 'title', 'description', 'author']
        read_only_fields = ['id', 'author']


class DetailApprovalRouteSerializer(serializers.ModelSerializer):
    """
    Детальная сериализация маршрута согласования
    """
    steps = ApproveStepSerializer(many=True)
    class Meta:
        model = ApprovalRoute
        fields = ['id', 'title', 'description', 'author', 'steps']
        readline_only_fields = ['id', 'author']


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


class UpdateApprovalRouteSerializer(serializers.ModelSerializer):
    """
    Обновление маршрута согласования
    """
    class Meta:
        model = ApprovalRoute
        fields = ['id', 'title', 'description', 'author']
        read_only_fields = ['id', 'author']