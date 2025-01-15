from rest_framework import serializers

from ..models import TaskTemplate

class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'title', 'description','group', 'dedlin', 'complexity']
        read_only_fields = ['id']

class ListTaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'title', 'description', 'group', 'dedlin', 'complexity']
        read_only_fields = ['id']


class DetailTaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = ['id', 'title', 'description', 'group', 'dedlin', 'complexity']
        read_only_fields = ['id']