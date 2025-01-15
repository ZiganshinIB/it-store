from rest_framework import serializers
from ..models import RequestTaskRelation

class RequestTaskRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTaskRelation
        fields = ['request', 'task', 'additional_info']