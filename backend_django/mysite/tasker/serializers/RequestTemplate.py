from rest_framework import serializers
from ..models import RequestTemplate
from . import TaskTemplateSerializer, DetailApprovalRouteSerializer

class ListRequestTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTemplate
        fields = ['id', 'title', 'description', 'image', 'dedline', 'approval_route']


class DetailRequestTemplateSerializer(serializers.ModelSerializer):
    tasks = TaskTemplateSerializer(many=True, required=False)
    approval_route = DetailApprovalRouteSerializer(read_only=True, required=False)
    class Meta:
        model = RequestTemplate
        fields = ['id', 'title', 'description', 'image', 'dedline', 'approval_route', 'tasks']

class UpdateRequestTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTemplate
        fields = ['id', 'title', 'description', 'image', 'dedline', 'approval_route']
